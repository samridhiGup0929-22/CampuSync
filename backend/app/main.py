import os, uuid, enum
from datetime import datetime, date, time, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import bcrypt, jwt
from pydantic import BaseModel, Field
from sqlalchemy import inspect as sa_inspect, text as sa_text, create_engine, Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from dotenv import load_dotenv

load_dotenv()
IST=timezone(timedelta(hours=5,minutes=30))  # campus local time (India has no DST)
def to_campus(dt):
    """Normalise any incoming datetime to naive campus-local (IST) time, the way the DB stores it."""
    if dt is None: return dt
    return dt.astimezone(IST).replace(tzinfo=None) if dt.tzinfo else dt
def campus_now(): return datetime.now(IST).replace(tzinfo=None)
DATABASE_URL=os.getenv("DATABASE_URL","sqlite:///./campus.db")
engine=create_engine(DATABASE_URL, connect_args={"check_same_thread":False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal=sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base=declarative_base()
class _Pwd:
    """bcrypt wrapper (passlib is unmaintained and breaks with bcrypt>=4.1 / Python 3.13+)."""
    @staticmethod
    def hash(p:str)->str: return bcrypt.hashpw(p.encode()[:72],bcrypt.gensalt()).decode()
    @staticmethod
    def verify(p:str,h:str)->bool:
        try: return bcrypt.checkpw(p.encode()[:72],h.encode())
        except Exception: return False
pwd=_Pwd()
oauth2=OAuth2PasswordBearer(tokenUrl="/api/auth/login")
SECRET=os.getenv("JWT_SECRET","dev-only-change-me")
ALGORITHM="HS256"

class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True)
    name=Column(String,nullable=False)
    email=Column(String,unique=True,index=True,nullable=False)
    password_hash=Column(String,nullable=False)
    role=Column(String,nullable=False)
    roll_number=Column(String,unique=True,index=True)
    branch=Column(String); year=Column(String); section=Column(String); batch=Column(String); dob=Column(String)
    department=Column(String)

class Room(Base):
    __tablename__="rooms"
    id=Column(Integer,primary_key=True)
    building=Column(String,index=True); floor=Column(String); name=Column(String,unique=True,index=True)
    capacity=Column(Integer,default=0); facilities=Column(String,default="")
    exam_suitable=Column(Boolean,default=False); permitted=Column(Boolean,default=True)
    data_status=Column(String,default="DEMO/VERIFY")
    room_type=Column(String,default="classroom"); mapped=Column(Boolean,default=False)
    rect=Column(String,default=""); note=Column(Text,default=""); aliases=Column(String,default="")

class CampusClass(Base):
    __tablename__="classes"
    id=Column(Integer,primary_key=True)
    subject=Column(String); subject_code=Column(String,default="DEMO")
    faculty_id=Column(Integer,ForeignKey("users.id")); branch=Column(String); year=Column(String); section=Column(String); batch=Column(String)
    room_id=Column(Integer,ForeignKey("rooms.id")); starts=Column(DateTime,index=True); ends=Column(DateTime)
    status=Column(String,default="PUBLISHED")
    faculty=relationship("User"); room=relationship("Room")

class FacultyRequest(Base):
    __tablename__="faculty_requests"
    id=Column(Integer,primary_key=True)
    request_code=Column(String,unique=True,index=True); faculty_id=Column(Integer,ForeignKey("users.id"))
    subject=Column(String); branch=Column(String); year=Column(String); section=Column(String); batch=Column(String)
    starts=Column(DateTime); ends=Column(DateTime); attendance=Column(Integer); preferred_building=Column(String)
    preferred_room=Column(String); purpose=Column(String); facilities=Column(String); remarks=Column(Text)
    status=Column(String,default="PENDING"); decision_reason=Column(Text,default="")
    allocated_room_id=Column(Integer,ForeignKey("rooms.id"),nullable=True)
    created_at=Column(DateTime,default=datetime.utcnow)
    faculty=relationship("User"); room=relationship("Room",foreign_keys=[allocated_room_id])

class Exam(Base):
    __tablename__="exams"
    id=Column(Integer,primary_key=True)
    name=Column(String); subject=Column(String); subject_code=Column(String); branch=Column(String); year=Column(String); section=Column(String)
    starts=Column(DateTime); ends=Column(DateTime); reporting=Column(DateTime); release_override=Column(DateTime,nullable=True)
    status=Column(String,default="PUBLISHED")

class Seat(Base):
    __tablename__="seats"
    id=Column(Integer,primary_key=True)
    exam_id=Column(Integer,ForeignKey("exams.id"),index=True); student_id=Column(Integer,ForeignKey("users.id"),index=True)
    room_id=Column(Integer,ForeignKey("rooms.id")); seat_number=Column(String)
    exam=relationship("Exam"); student=relationship("User"); room=relationship("Room")

class Announcement(Base):
    __tablename__="announcements"
    id=Column(Integer,primary_key=True); title=Column(String); body=Column(Text); audience=Column(String,default="ALL")
    branch=Column(String,default=""); created_at=Column(DateTime,default=datetime.utcnow)

class Report(Base):
    __tablename__="reports"
    id=Column(Integer,primary_key=True); student_id=Column(Integer,ForeignKey("users.id"))
    category=Column(String); message=Column(Text); status=Column(String,default="OPEN"); admin_note=Column(Text,default="")
    created_at=Column(DateTime,default=datetime.utcnow); student=relationship("User")

class LibraryPass(Base):
    __tablename__="library_passes"
    id=Column(Integer,primary_key=True); pass_code=Column(String,unique=True,index=True)
    student_id=Column(Integer,ForeignKey("users.id")); purpose=Column(String); valid_from=Column(DateTime); valid_until=Column(DateTime)
    active=Column(Boolean,default=True); student=relationship("User")

class Audit(Base):
    __tablename__="audit_logs"
    id=Column(Integer,primary_key=True); actor_id=Column(Integer); action=Column(String); detail=Column(Text); created_at=Column(DateTime,default=datetime.utcnow)

Base.metadata.create_all(engine)

def ensure_schema():
    """Additive, non-destructive schema update so existing campus.db files keep their data."""
    insp=sa_inspect(engine); have={c['name'] for c in insp.get_columns('rooms')}
    adds={"room_type":"VARCHAR DEFAULT 'classroom'","mapped":"BOOLEAN DEFAULT 0","rect":"VARCHAR DEFAULT ''","note":"TEXT DEFAULT ''","aliases":"VARCHAR DEFAULT ''"}
    with engine.begin() as conn:
        for col,ddl in adds.items():
            if col not in have: conn.execute(sa_text(f"ALTER TABLE rooms ADD COLUMN {col} {ddl}"))
ensure_schema()

def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()

def audit(db,user,action,detail):
    db.add(Audit(actor_id=user.id,action=action,detail=detail)); db.commit()

def seed(db):
    if db.query(User).count(): return
    demo=[
      ("Demo Administrator","admin@ddugu.demo","admin"),
      ("Demo Faculty","faculty@ddugu.demo","faculty"),
      ("Demo Student","student@ddugu.demo","student")]
    users=[]
    for name,email,role in demo:
        u=User(name=name,email=email,password_hash=pwd.hash("Campus@123"),role=role,
               roll_number="DEMO2026CSE001" if role=="student" else None,
               branch="CSE" if role=="student" else None,year="Second Year" if role=="student" else None,
               section="A" if role=="student" else None,batch="A1" if role=="student" else None,
               dob="2004-08-15" if role=="student" else None,department="CSE" if role=="faculty" else None)
        db.add(u); users.append(u)
    db.flush()
    # Room names and floor labels are based on the written brief; capacities are demo estimates pending verification.
    rooms=[
      ("IET","Ground Floor","Library",160,"Reading,Exam",True),
      ("IET","First Floor","IET20",75,"Projector,Whiteboard",True),
      ("IET","First Floor","IET18",75,"Projector,Whiteboard",True),
      ("IET","First Floor","IET19",75,"Projector,Whiteboard",True),
      ("IET","First Floor","IET17",75,"Projector,Whiteboard",True),
      ("IET","Second Floor","IET32",200,"Projector,Audio",True),
      ("IET","Second Floor","IET24",60,"Projector",True),
      ("IET","Second Floor","IET25",60,"Projector",True),
      ("IET","Second Floor","IET29",60,"Projector",True),
      ("IET","Second Floor","IET30",60,"Projector",True),
      ("IET","Second Floor","IET28",60,"Projector",True)]
    for n in range(1,13):
        rooms.append(("Deeksha Bhawan","Ground Floor" if n<=7 else "First Floor",f"LH{n:02d}",60,"Whiteboard",True))
    # Additional blueprint labels are included only as verify/configure entries.
    for name in ["IET22","IET16","IET14","IET15","IET23","LH13","LH14"]:
        rooms.append(("IET" if name.startswith("IET") else "Deeksha Bhawan","VERIFY",name,0,"",False))
    for b,f,n,c,fac,exam in rooms:
        db.add(Room(building=b,floor=f,name=n,capacity=c,facilities=fac,exam_suitable=exam,permitted=True,
                    data_status="DEMO/VERIFY" if c==0 or n in ("IET24","IET25","IET29","IET30","IET28") else "DEMO"))
    db.flush()
    # Demo timetable: one scheduled class on a date to make student workflow visible.
    faculty=users[1]; student=users[2]
    today=datetime.now().date()
    r=db.query(Room).filter_by(name="IET20").first()
    db.add(CampusClass(subject="Data Structures",subject_code="CS201",faculty_id=faculty.id,branch="CSE",year="Second Year",section="A",batch="A1",
                       room_id=r.id,starts=datetime.combine(today,time(9,0)),ends=datetime.combine(today,time(10,0))))
    db.add(Announcement(title="Welcome to DDUGU Smart Campus",body="This is a DEMO/TEST announcement. Official notices must be published by authorised administrators.",audience="ALL"))
    db.commit()

def sync_rooms(db):
    """Upsert blueprint-derived fields. Never overwrites admin-edited capacity/facilities of existing rooms."""
    import json
    from .campus_data import ROOMS
    for d in ROOMS:
        r=db.query(Room).filter_by(name=d["name"]).first()
        if not r:
            r=Room(name=d["name"],building=d["building"],capacity=d["capacity"],facilities=d["facilities"],
                   exam_suitable=d["type"] in ("classroom","hall","library") and d["capacity"]>0,permitted=d["capacity"]>0,data_status=d["status"])
            db.add(r)
        r.building=d["building"]; r.floor=d["floor"]; r.room_type=d["type"]; r.mapped=d["mapped"]
        r.rect=json.dumps(d["rect"]) if d["rect"] else ""; r.note=d["note"]; r.aliases=",".join(d["aliases"])
    db.commit()

app=FastAPI(title="DDUGU Smart Campus API",version="1.0.0")
origins=os.getenv("CORS_ORIGINS","http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.on_event("startup")
def startup():
    db=SessionLocal()
    try: seed(db); sync_rooms(db)
    finally: db.close()

def current_user(token:str=Depends(oauth2),db:Session=Depends(get_db)):
    try:
        payload=jwt.decode(token,SECRET,algorithms=[ALGORITHM]); uid=int(payload["sub"])
    except Exception: raise HTTPException(401,"Invalid or expired session")
    user=db.get(User,uid)
    if not user: raise HTTPException(401,"User not found")
    return user

def require(*roles):
    def checker(user=Depends(current_user)):
        if user.role not in roles: raise HTTPException(403,"Insufficient permissions")
        return user
    return checker

def token_for(u):
    exp=datetime.now(timezone.utc)+timedelta(minutes=int(os.getenv("JWT_EXPIRE_MINUTES","720")))
    return jwt.encode({"sub":str(u.id),"role":u.role,"exp":exp},SECRET,algorithm=ALGORITHM)

def serialize_room(r):
    return {"id":r.id,"name":r.name,"building":r.building,"floor":r.floor,"capacity":r.capacity,"facilities":r.facilities.split(",") if r.facilities else [],"exam_suitable":r.exam_suitable,"permitted":r.permitted,"data_status":r.data_status,"type":r.room_type or "classroom","mapped":bool(r.mapped),"rect":__import__("json").loads(r.rect) if r.rect else None,"note":r.note or ""}

@app.get("/health")
def health(): return {"status":"ok","service":"DDUGU Smart Campus API"}

from pydantic import field_validator
class _Local(BaseModel):
    @field_validator("starts","ends","reporting","valid_from","valid_until",check_fields=False,mode="after")
    @classmethod
    def _ist(cls,v): return to_campus(v)

class LoginIn(BaseModel):
    email:str; password:str
class RequestIn(_Local):
    subject:str; branch:str; year:str; section:str=""; batch:str=""
    starts:datetime; ends:datetime; attendance:int=Field(gt=0)
    preferred_building:str="Any"; preferred_room:str=""; purpose:str="Extra class"; facilities:list[str]=[]
    remarks:str=""
class DecisionIn(BaseModel):
    decision:str; room_id:Optional[int]=None; reason:str=""
class ClassIn(_Local):
    subject:str; subject_code:str="DEMO"; faculty_id:int; branch:str; year:str; section:str=""
    batch:str=""; room_id:int; starts:datetime; ends:datetime
class ExamIn(_Local):
    name:str; subject:str; subject_code:str="DEMO"; branch:str; year:str; section:str=""
    starts:datetime; ends:datetime; reporting:datetime; room_ids:list[int]
class ExamLookup(BaseModel):
    roll_number:str; branch:str; year:str; dob:str
class AnnouncementIn(BaseModel):
    title:str; body:str; audience:str="ALL"; branch:str=""
class ReportIn(BaseModel):
    category:str; message:str
class PassIn(_Local):
    roll_number:str; purpose:str; valid_from:datetime; valid_until:datetime

@app.post("/api/auth/login")
def login(data:LoginIn,db:Session=Depends(get_db)):
    u=db.query(User).filter_by(email=data.email.lower()).first()
    if not u or not pwd.verify(data.password,u.password_hash): raise HTTPException(401,"Incorrect email or password")
    return {"access_token":token_for(u),"token_type":"bearer","user":{"id":u.id,"name":u.name,"email":u.email,"role":u.role,"roll_number":u.roll_number,"branch":u.branch,"year":u.year,"section":u.section}}

@app.get("/api/me")
def me(u=Depends(current_user)):
    return {"id":u.id,"name":u.name,"email":u.email,"role":u.role,"roll_number":u.roll_number,"branch":u.branch,"year":u.year,"section":u.section}

@app.get("/api/rooms")
def rooms(db:Session=Depends(get_db),u=Depends(current_user)):
    return [serialize_room(r) for r in db.query(Room).order_by(Room.building,Room.name).all()]

@app.get("/api/rooms/available")
def available(starts:datetime,ends:datetime,capacity:int=1,building:str="Any",db:Session=Depends(get_db),u=Depends(current_user)):
    starts,ends=to_campus(starts),to_campus(ends)
    if ends<=starts: raise HTTPException(400,"End time must be after start time")
    result=[]
    for r in db.query(Room).filter(Room.permitted==True,Room.capacity>=capacity).all():
        if building!="Any" and r.building!=building: continue
        conflict=db.query(CampusClass).filter(CampusClass.room_id==r.id,CampusClass.status=="PUBLISHED",CampusClass.starts<ends,CampusClass.ends>starts).first()
        if not conflict: result.append(serialize_room(r))
    return result

@app.get("/api/classes")
def list_classes(db:Session=Depends(get_db),u=Depends(current_user)):
    q=db.query(CampusClass)
    if u.role=="student": q=q.filter(CampusClass.branch==u.branch,CampusClass.year==u.year,CampusClass.section==u.section)
    if u.role=="faculty": q=q.filter(CampusClass.faculty_id==u.id)
    return [{"id":c.id,"subject":c.subject,"subject_code":c.subject_code,"faculty":c.faculty.name,"branch":c.branch,"year":c.year,"section":c.section,"starts":c.starts.isoformat(),"ends":c.ends.isoformat(),"room":c.room.name,"building":c.room.building,"floor":c.room.floor,"status":c.status} for c in q.order_by(CampusClass.starts).all()]

@app.post("/api/requests")
def create_request(data:RequestIn,db:Session=Depends(get_db),u=Depends(require("faculty"))):
    if data.ends<=data.starts: raise HTTPException(400,"End time must be after start time")
    code="REQ-"+uuid.uuid4().hex[:8].upper()
    r=FacultyRequest(request_code=code,faculty_id=u.id,subject=data.subject,branch=data.branch,year=data.year,section=data.section,batch=data.batch,
      starts=data.starts,ends=data.ends,attendance=data.attendance,preferred_building=data.preferred_building,preferred_room=data.preferred_room,
      purpose=data.purpose,facilities=",".join(data.facilities),remarks=data.remarks)
    db.add(r); db.commit(); audit(db,u,"REQUEST_CREATED",code)
    return {"request_id":code,"status":"PENDING"}

@app.get("/api/requests")
def list_requests(db:Session=Depends(get_db),u=Depends(current_user)):
    q=db.query(FacultyRequest)
    if u.role=="faculty": q=q.filter(FacultyRequest.faculty_id==u.id)
    elif u.role!="admin": raise HTTPException(403,"Not allowed")
    return [{"id":r.id,"request_id":r.request_code,"faculty":r.faculty.name,"subject":r.subject,"branch":r.branch,"year":r.year,"section":r.section,
      "starts":r.starts.isoformat(),"ends":r.ends.isoformat(),"attendance":r.attendance,"status":r.status,"reason":r.decision_reason} for r in q.order_by(FacultyRequest.created_at.desc()).all()]

def room_conflict(db,room_id,starts,ends,ignore_class=None):
    q=db.query(CampusClass).filter(CampusClass.room_id==room_id,CampusClass.status=="PUBLISHED",CampusClass.starts<ends,CampusClass.ends>starts)
    if ignore_class: q=q.filter(CampusClass.id!=ignore_class)
    return q.first()

@app.post("/api/requests/{request_id}/decision")
def decide(request_id:int,data:DecisionIn,db:Session=Depends(get_db),u=Depends(require("admin"))):
    r=db.get(FacultyRequest,request_id)
    if not r: raise HTTPException(404,"Request not found")
    if r.status!="PENDING": raise HTTPException(409,"Request already processed")
    if data.decision=="approve":
        room=db.get(Room,data.room_id) if data.room_id else None
        if not room or not room.permitted: raise HTTPException(400,"Choose a permitted room")
        if room.capacity<r.attendance: raise HTTPException(400,"Room capacity is insufficient")
        if room_conflict(db,room.id,r.starts,r.ends): raise HTTPException(409,"Room booking conflict")
        if db.query(CampusClass).filter(CampusClass.faculty_id==r.faculty_id,CampusClass.status=="PUBLISHED",CampusClass.starts<r.ends,CampusClass.ends>r.starts).first():
            raise HTTPException(409,"Faculty member already has a class in this time window")
        c=CampusClass(subject=r.subject,subject_code="DEMO",faculty_id=r.faculty_id,branch=r.branch,year=r.year,section=r.section,batch=r.batch,
                      room_id=room.id,starts=r.starts,ends=r.ends)
        db.add(c); r.status="APPROVED"; r.allocated_room_id=room.id; r.decision_reason=data.reason or "Approved"
    elif data.decision=="reject":
        r.status="REJECTED"; r.decision_reason=data.reason or "Rejected by administrator"
    else: raise HTTPException(400,"Decision must be approve or reject")
    db.commit(); audit(db,u,"REQUEST_"+data.decision.upper(),r.request_code)
    return {"status":r.status,"request_id":r.request_code}

@app.post("/api/classes")
def create_class(data:ClassIn,db:Session=Depends(get_db),u=Depends(require("admin"))):
    if data.ends<=data.starts: raise HTTPException(400,"Invalid time interval")
    room=db.get(Room,data.room_id); faculty=db.get(User,data.faculty_id)
    if not room or not faculty or faculty.role!="faculty": raise HTTPException(400,"Invalid room or faculty")
    if room_conflict(db,room.id,data.starts,data.ends): raise HTTPException(409,"Room conflict")
    fc=db.query(CampusClass).filter(CampusClass.faculty_id==faculty.id,CampusClass.status=="PUBLISHED",CampusClass.starts<data.ends,CampusClass.ends>data.starts).first()
    if fc: raise HTTPException(409,"Faculty is already scheduled")
    c=CampusClass(**data.model_dump()); db.add(c); db.commit(); audit(db,u,"CLASS_CREATED",str(c.id))
    return {"id":c.id,"status":"PUBLISHED"}

@app.get("/api/announcements")
def announcements(db:Session=Depends(get_db),u=Depends(current_user)):
    q=db.query(Announcement)
    if u.role=="student": q=q.filter((Announcement.audience=="ALL") | (Announcement.branch==u.branch))
    return [{"id":a.id,"title":a.title,"body":a.body,"created_at":a.created_at.isoformat()} for a in q.order_by(Announcement.created_at.desc()).all()]

@app.post("/api/announcements")
def add_announcement(data:AnnouncementIn,db:Session=Depends(get_db),u=Depends(require("admin"))):
    a=Announcement(**data.model_dump()); db.add(a); db.commit(); audit(db,u,"ANNOUNCEMENT_PUBLISHED",a.title); return {"id":a.id}

@app.post("/api/reports")
def report(data:ReportIn,db:Session=Depends(get_db),u=Depends(require("student"))):
    r=Report(student_id=u.id,category=data.category,message=data.message); db.add(r); db.commit(); return {"id":r.id,"status":r.status}

@app.get("/api/reports")
def reports(db:Session=Depends(get_db),u=Depends(require("admin"))):
    return [{"id":r.id,"student":r.student.name,"roll_number":r.student.roll_number,"category":r.category,"message":r.message,"status":r.status} for r in db.query(Report).order_by(Report.created_at.desc()).all()]

@app.post("/api/exams")
def create_exam(data:ExamIn,db:Session=Depends(get_db),u=Depends(require("admin"))):
    if data.ends<=data.starts: raise HTTPException(400,"Invalid exam time")
    students=db.query(User).filter(User.role=="student",User.branch==data.branch,User.year==data.year).all()
    if not students: raise HTTPException(400,"No matching demo/imported students found")
    selected=[db.get(Room,i) for i in data.room_ids]
    if any(not r or not r.exam_suitable or not r.permitted for r in selected): raise HTTPException(400,"All rooms must be permitted and exam-suitable")
    if sum(r.capacity for r in selected)<len(students): raise HTTPException(400,"Selected rooms do not have enough total capacity")
    for r in selected:
        if room_conflict(db,r.id,data.starts,data.ends): raise HTTPException(409,f"Room conflict: {r.name}")
    exam=Exam(name=data.name,subject=data.subject,subject_code=data.subject_code,branch=data.branch,year=data.year,section=data.section,starts=data.starts,ends=data.ends,reporting=data.reporting)
    db.add(exam); db.flush()
    idx=0
    for room in selected:
        for seat in range(1,room.capacity+1):
            if idx>=len(students): break
            db.add(Seat(exam_id=exam.id,student_id=students[idx].id,room_id=room.id,seat_number=f"{room.name}-{seat:03d}")); idx+=1
    db.commit(); audit(db,u,"EXAM_CREATED_AND_ALLOCATED",str(exam.id))
    return {"exam_id":exam.id,"students_allocated":idx,"release_at":(exam.starts-timedelta(hours=1)).isoformat()}

@app.post("/api/exams/lookup")
def exam_lookup(data:ExamLookup,db:Session=Depends(get_db)):
    # Generic error avoids revealing which identity field was correct.
    student=db.query(User).filter(User.role=="student",User.roll_number==data.roll_number,User.branch==data.branch,User.year==data.year,User.dob==data.dob).first()
    if not student: raise HTTPException(404,"Details could not be verified")
    now=campus_now()
    seats=db.query(Seat).filter(Seat.student_id==student.id).all()
    if not seats: return {"message":"No published examination allocation found"}
    results=[]
    for s in seats:
        e=s.exam; release=e.release_override or (e.starts-timedelta(hours=1))
        base={"subject":e.subject,"subject_code":e.subject_code,"date":e.starts.date().isoformat(),"starts":e.starts.isoformat(),"ends":e.ends.isoformat(),"reporting":e.reporting.isoformat(),"status":e.status,"released":now>=release}
        if now>=release and e.status=="PUBLISHED":
            base.update({"building":s.room.building,"floor":s.room.floor,"room":s.room.name,"seat":s.seat_number})
        else: base["release_at"]=release.isoformat()
        results.append(base)
    return {"student":student.name,"roll_number":student.roll_number,"examinations":results}

@app.post("/api/library/passes")
def issue_pass(data:PassIn,db:Session=Depends(get_db),u=Depends(require("admin"))):
    student=db.query(User).filter_by(roll_number=data.roll_number,role="student").first()
    if not student: raise HTTPException(404,"Student not found")
    if data.valid_until<=data.valid_from: raise HTTPException(400,"Invalid validity window")
    p=LibraryPass(pass_code="LIB-"+uuid.uuid4().hex[:10].upper(),student_id=student.id,purpose=data.purpose,valid_from=data.valid_from,valid_until=data.valid_until)
    db.add(p); db.commit(); audit(db,u,"LIBRARY_PASS_ISSUED",p.pass_code); return {"pass_code":p.pass_code}

@app.get("/api/library/passes/me")
def my_passes(db:Session=Depends(get_db),u=Depends(require("student"))):
    return [{"pass_code":p.pass_code,"purpose":p.purpose,"valid_from":p.valid_from.isoformat(),"valid_until":p.valid_until.isoformat(),"active":p.active} for p in db.query(LibraryPass).filter_by(student_id=u.id).all()]

@app.post("/api/library/validate/{pass_code}")
def validate_pass(pass_code:str,db:Session=Depends(get_db),u=Depends(require("admin","faculty"))):
    p=db.query(LibraryPass).filter_by(pass_code=pass_code).first()
    now=campus_now()
    valid=bool(p and p.active and p.valid_from<=now<=p.valid_until)
    return {"valid":valid,"message":"Valid pass" if valid else "Invalid, expired or revoked pass"}

@app.get("/api/admin/overview")
def overview(db:Session=Depends(get_db),u=Depends(require("admin"))):
    now=campus_now()
    return {"students":db.query(User).filter_by(role="student").count(),"faculty":db.query(User).filter_by(role="faculty").count(),
      "rooms":db.query(Room).filter(Room.capacity>0).count(),"pending_requests":db.query(FacultyRequest).filter_by(status="PENDING").count(),
      "today_classes":db.query(CampusClass).filter(CampusClass.starts>=datetime.combine(now.date(),time.min),CampusClass.starts<datetime.combine(now.date()+timedelta(days=1),time.min)).count(),
      "exams":db.query(Exam).count(),"open_reports":db.query(Report).filter_by(status="OPEN").count()}

@app.get("/api/admin/audit")
def audit_list(db:Session=Depends(get_db),u=Depends(require("admin"))):
    return [{"action":a.action,"detail":a.detail,"created_at":a.created_at.isoformat()} for a in db.query(Audit).order_by(Audit.created_at.desc()).limit(100).all()]


from .campus_routes import build_router
app.include_router(build_router(Room,CampusClass,get_db,current_user,campus_now,serialize_room))
