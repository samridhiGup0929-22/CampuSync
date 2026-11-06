# DEVELOPMENT STATUS

_Last updated: 2026-11-06_

## What the existing project actually was (Phase 1 findings)
- Backend: single-file FastAPI app (`backend/app/main.py`, ~380 lines) - JWT auth, 3 roles, rooms, requests/approval,
  classes, exams + seat allocation, announcements, reports, library passes, audit log.
- Frontend: one dense `App.tsx` (all pages inline), light teal theme in `style.css`, **no router, no Leaflet, no SVG maps**.
  The "Campus Map" was an OpenStreetMap iframe; the "assistant" was hard-coded canned text with no backend calls.
- README describes more than exists (e.g. library QR is not implemented; CI had no tests).

## Completed and TESTED (8 backend tests pass: `cd backend && python -m pytest -q tests`)
- [x] **Startup crash fixed**: `passlib 1.7.4` + `bcrypt 5` raised `ValueError` during seeding on a fresh install.
      Now uses `bcrypt` directly; `python-jose` replaced by `PyJWT`. Requirements un-pinned to ranges for Python 3.14
      (**not yet run on 3.14** - sandbox has 3.12; CI matrix now includes 3.14).
- [x] **Timezone bug fixed**: browser sends UTC (`toISOString`); backend stored it as if local. All inputs are now
      normalised to IST; "now" for exam release / pass validity uses IST.
- [x] **Faculty double-booking now blocked at approval** (previously only on manual class creation).
- [x] **Blueprint data layer** (`backend/app/campus_data.py`): every room label printed on the PDF blueprint is traced to
      a clickable rectangle (overlay visually verified against the image). Blueprint asset:
      `frontend/public/blueprints/campus-blueprint.png`.
- [x] **Safe schema upgrade** (`ensure_schema` + `sync_rooms`): verified on an old-schema DB - data and admin-edited
      capacities preserved, VERIFY floors corrected from blueprint, missing rooms added.
- [x] **Campus API**: `GET /api/campus/{buildings,outdoor,rooms,search,route}` - rooms carry live current/next booking;
      routes are always flagged `approximate`.

## Known data conflicts (need a human decision - not guessed)
1. **Laboratories**: the brief lists CSE/ME/ECE/IT labs on IET first floor, but the blueprint draws **no labs** there
   (only IET22/16/14/15/20/19/18/17). Labs are searchable (First Floor) but `mapped=false`. Acceptance TEST 12 ("lab is
   highlighted") cannot be met honestly until an admin places them (planned: admin click-to-place tool).
2. Faculty Cabins and Administrative Office are not drawn on the blueprint -> unmapped.
3. IET22/16/14/15/23 and LH13/LH14 are on the blueprint, not in the written list -> kept visible, capacity 0, VERIFY.
4. Outdoor GPS: no surveyed coordinates supplied. Placeholders near Gorakhpur are exposed as `verified:false`.

## NOT done yet (remaining, in planned order)
- [ ] Frontend: component split, black/orange design system, landing page
- [ ] Leaflet outdoor map + SVG indoor map UI (floor/building selector, search, click-to-detail, route overlay)
- [ ] "DDUGU Campus AI": backend `/api/assistant` (intent -> real data, optional LLM via server-side key) + floating UI
- [ ] Room finder: alternative rooms/time slots with reasons (cross-building fallback)
- [ ] Exam management: reschedule/cancel/publish, per-room allocation summary; capacity already enforced
- [ ] CSV/XLSX student import + validation + error report + export (`openpyxl` already in requirements)
- [ ] In-app notifications; report status updates; admin room/coordinate configuration
- [ ] Frontend production build verification, mobile checks, Docker on Python 3.14, README refresh

## Commands
```
cd backend && python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt && cp .env.example .env
uvicorn app.main:app --reload --port 8000
python -m pytest -q tests
cd ../frontend && npm install && npm run dev
```

## Modified / new files
`backend/app/main.py` (patched), `backend/app/campus_data.py` (new), `backend/app/campus_routes.py` (new),
`backend/requirements.txt`, `backend/tests/*` (new), `frontend/public/blueprints/campus-blueprint.png` (new),
`.github/workflows/ci.yml`, `DEVELOPMENT_STATUS.md`

## Next task
Split `App.tsx` into components and build the indoor map view against `/api/campus/*`.
