# DDUGU Smart Campus — Working Demo Prototype

A hackathon-ready, role-based campus coordination prototype for IET and Deeksha Bhawan.

## Important data note
The supplied problem statement asks teams to use official student datasets and blueprints. No student CSV/XLSX dataset was attached. The supplied PDF includes the campus blueprint (see `docs/`). All seeded accounts, students, schedules, bookings and capacities are explicitly **DEMO/TEST DATA**, not verified university records. Room capacities and map positions are configurable and must be confirmed by DDUGU before operational use.

The PDF blueprint visually includes additional labels (including IET22/IET16/IET14/IET15/IET23 and LH13/LH14) that differ from the simplified room list in the written prompt. They are seeded as `VERIFY` rooms where relevant, not asserted as verified inventory.

## Stack
- Frontend: React + TypeScript + Vite
- Backend: FastAPI + SQLAlchemy + SQLite (PostgreSQL URL supported)
- Authentication: JWT bearer tokens + bcrypt password hashing
- Scheduling: backend overlap/capacity/usage validation
- DevOps: Docker Compose + GitHub Actions test workflow

## Demo accounts
Password for all accounts: `Campus@123`
- Admin: `admin@ddugu.demo`
- Faculty: `faculty@ddugu.demo`
- Student: `student@ddugu.demo`

The student demo account is `DEMO2026CSE001`. Use it only with the demo login. Examination lookup requires roll number, branch, academic year and DOB, and exam venue/seat stays hidden until 60 minutes before the exam (server time).

## Run locally

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Open http://localhost:5173

### Docker
From the project root:
```bash
docker compose up --build
```
Frontend: http://localhost:5173 ; API: http://localhost:8000

## Implemented demo workflows
- Role-specific student, faculty and administrator views
- JWT login and server-side role checks
- Room search across both buildings and time windows
- Faculty requests with unique IDs and pending status
- Admin approval/rejection with room conflict and capacity checks
- Manual class creation and schedule listing
- Examination creation and deterministic seat allocation without exceeding capacity
- Secure student exam lookup and one-hour-before-release rule
- Announcements, student issue reports, library pass issuance/validation
- Audit history and demo campus room explorer
- Public project landing page with persistent orange-on-white / orange-on-black themes
- Blueprint-based block selector for IET and Deeksha Bhawan with schematic start-to-destination routes; department assignments and route geometry still require university verification
- OpenStreetMap campus view alongside the block diagram; department and Dean's Office pins are intentionally omitted until verified location data is available
- Campus assistant supports preset English, Hindi, and Hinglish answers for map, room, timetable, library, exam, and announcement questions
- Health endpoint and API documentation

## API highlights
- `POST /api/auth/login`
- `GET /api/rooms/available`
- `POST /api/requests` (faculty)
- `GET /api/requests` (faculty sees own; admin sees all)
- `POST /api/requests/{id}/decision` (admin)
- `GET/POST /api/classes` (admin write)
- `POST /api/exams` (admin; creates seat allocations)
- `POST /api/exams/lookup`
- `GET/POST /api/announcements`
- `POST /api/reports`; `GET /api/reports` (admin)
- `POST /api/library/passes` (admin); `GET /api/library/passes/me`
- `POST /api/library/validate/{pass_id}`

## Before real deployment
1. Import verified university student/faculty records and confirm room capacities, floor assignments and room permissions.
2. Configure PostgreSQL, HTTPS, secure secret management, backups, monitoring and production CORS.
3. Add institutional identity verification/SSO, email/SMS/push notification provider, import validation and formal data governance.
4. Have DDUGU administrators validate blueprint mappings and all exam allocation rules.
5. Run security, privacy, load and accessibility reviews. This is a demo prototype, not an officially approved university system.
