"""Campus navigation endpoints (blueprint-driven). Built via a factory to avoid circular imports with main.py."""
import re
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import campus_data as cd


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def build_router(Room, CampusClass, get_db, current_user, campus_now, serialize_room):
    router = APIRouter(prefix="/api/campus", tags=["campus"])

    def booking_state(db, room, at):
        cur = db.query(CampusClass).filter(CampusClass.room_id == room.id, CampusClass.status == "PUBLISHED",
                                           CampusClass.starts <= at, CampusClass.ends > at).first()
        nxt = db.query(CampusClass).filter(CampusClass.room_id == room.id, CampusClass.status == "PUBLISHED",
                                           CampusClass.starts > at, CampusClass.starts < at + timedelta(days=1)
                                           ).order_by(CampusClass.starts).first()
        fmt = lambda c: None if not c else {"subject": c.subject, "faculty": c.faculty.name,
                                            "starts": c.starts.isoformat(), "ends": c.ends.isoformat()}
        if room.capacity <= 0:
            availability = "VERIFY"
        else:
            availability = "OCCUPIED" if cur else "AVAILABLE"
        return {"availability": availability, "current": fmt(cur), "next": fmt(nxt)}

    def detail(db, r, at):
        d = serialize_room(r)
        d.update(booking_state(db, r, at))
        d["aliases"] = [a for a in (r.aliases or "").split(",") if a]
        return d

    @router.get("/buildings")
    def buildings(u=Depends(current_user)):
        out = {}
        for (b, f), info in cd.FLOORS.items():
            out.setdefault(b, {"name": b, "floors": []})["floors"].append(
                {"floor": f, "view": list(info["view"]), "entrance": info["entrance"], "stairs": info["stairs"]})
        for b in out.values():
            b["floors"].sort(key=lambda x: cd.FLOOR_ORDER[x["floor"]])
        return {"image": cd.BLUEPRINT_IMAGE, "image_size": list(cd.BLUEPRINT_SIZE),
                "buildings": list(out.values()), "features": [
                    {**f, "at": list(f["at"])} for f in cd.FEATURES],
                "inter_building": cd.INTER_BUILDING,
                "geometry_note": "Room outlines are traced from the supplied blueprint and are approximate."}

    @router.get("/outdoor")
    def outdoor(u=Depends(current_user)):
        o = cd.OUTDOOR_DEFAULTS
        return {"centre": list(o["centre"]), "zoom": o["zoom"], "verified": o["verified"], "points": o["points"],
                "inter_building_metres": cd.INTER_BUILDING["approx_metres"],
                "warning": "No surveyed coordinates were supplied. Positions are approximate placeholders "
                           "until an administrator verifies them."}

    @router.get("/rooms")
    def rooms(building: Optional[str] = None, floor: Optional[str] = None,
              db: Session = Depends(get_db), u=Depends(current_user)):
        q = db.query(Room)
        if building: q = q.filter(Room.building == building)
        if floor: q = q.filter(Room.floor == floor)
        at = campus_now()
        return [detail(db, r, at) for r in q.order_by(Room.building, Room.floor, Room.name).all()]

    def find(db, query):
        n = _norm(query)
        if not n: return []
        scored = []
        for r in db.query(Room).all():
            names = [_norm(r.name)] + [_norm(a) for a in (r.aliases or "").split(",") if a]
            if n in names: score = 100
            elif any(n in x or x in n for x in names if len(x) >= 3): score = 60
            else: continue
            scored.append((score, r))
        scored.sort(key=lambda t: (-t[0], t[1].building, t[1].name))
        return [r for _, r in scored]

    @router.get("/search")
    def search(q: str, db: Session = Depends(get_db), u=Depends(current_user)):
        at = campus_now()
        results = [detail(db, r, at) for r in find(db, q)]
        if results:
            return {"query": q, "kind": "room", "best": results[0], "results": results}
        n = _norm(q)
        for b in ("IET", "Deeksha Bhawan"):
            if n and (n in _norm(b) or (n == "deeksha")):
                return {"query": q, "kind": "building", "best": None, "results": [],
                        "building": {"name": b, "default_floor": "Ground Floor"}}
        return {"query": q, "kind": "none", "best": None, "results": []}

    @router.get("/route")
    def route(to: str, from_building: Optional[str] = None, db: Session = Depends(get_db), u=Depends(current_user)):
        matches = find(db, to)
        if not matches: raise HTTPException(404, "Destination not found in campus data")
        r = matches[0]
        steps, outdoor = [], None
        if from_building and from_building != r.building and {from_building, r.building} == {"IET", "Deeksha Bhawan"}:
            outdoor = cd.INTER_BUILDING["approx_metres"]
            steps.append(f"Walk from {from_building} to {r.building} (approx. {outdoor} m, per the problem statement)")
        steps.append(f"Enter {r.building} through the Entry Gate (Ground Floor)")
        if r.floor != "Ground Floor":
            steps.append(f"Take the stairs to the {r.floor}")
        if not r.mapped:
            steps.append(f"{r.name}: position is not drawn on the blueprint — ask the department or an administrator")
            return {"destination": r.name, "building": r.building, "floor": r.floor, "approximate": True,
                    "available": False, "polyline": None, "steps": steps, "outdoor_metres": outdoor,
                    "note": "Indoor route unavailable: this room is not shown on the supplied blueprint."}
        import json
        rect = json.loads(r.rect)
        info = cd.FLOORS[(r.building, r.floor)]
        start = info["entrance"] or info["stairs"]
        poly = cd.route_in_floor(r.building, r.floor, rect, start)
        steps.append(f"Follow the corridor to {r.name}")
        return {"destination": r.name, "building": r.building, "floor": r.floor, "approximate": True,
                "available": True, "polyline": [list(p) for p in poly], "steps": steps, "outdoor_metres": outdoor,
                "note": "Approximate route traced on the blueprint; it is not a surveyed indoor path."}

    return router
