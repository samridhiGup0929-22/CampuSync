def room_id(client, h, name):
    return next(r["id"] for r in client.get("/api/rooms", headers=h).json() if r["name"] == name)

def req(subject, start, end, n=70):
    return dict(subject=subject, branch="CSE", year="Second Year", section="A", batch="A1",
                starts=start, ends=end, attendance=n)

def test_login_and_roles(client, admin, student):
    assert client.get("/api/admin/overview", headers=admin).json()["rooms"] > 0
    assert client.get("/api/admin/overview", headers=student).status_code == 403
    assert client.post("/api/auth/login", json={"email": "admin@ddugu.demo", "password": "bad"}).status_code == 401

def test_utc_input_is_stored_as_ist(client, faculty, admin):
    # 05:30Z == 11:00 IST
    r = client.post("/api/requests", json=req("TZ", "2026-12-01T05:30:00.000Z", "2026-12-01T06:30:00.000Z"), headers=faculty)
    assert r.status_code == 200
    rows = client.get("/api/requests", headers=admin).json()
    assert any(x["starts"].startswith("2026-12-01T11:00") for x in rows)

def test_overlap_blocked_and_faculty_conflict(client, faculty, admin):
    a, b = room_id(client, admin, "IET20"), room_id(client, admin, "IET19")
    s, e = "2026-12-02T05:30:00Z", "2026-12-02T06:30:00Z"
    ids = []
    for i in range(3):
        client.post("/api/requests", json=req(f"R{i}", s, e), headers=faculty)
    pend = [x["id"] for x in client.get("/api/requests", headers=admin).json() if x["status"] == "PENDING" and x["subject"].startswith("R")]
    assert client.post(f"/api/requests/{pend[0]}/decision", json={"decision": "approve", "room_id": a}, headers=admin).status_code == 200
    # same room -> room conflict
    assert client.post(f"/api/requests/{pend[1]}/decision", json={"decision": "approve", "room_id": a}, headers=admin).status_code == 409
    # different room, same faculty & time -> faculty conflict
    r = client.post(f"/api/requests/{pend[2]}/decision", json={"decision": "approve", "room_id": b}, headers=admin)
    assert r.status_code == 409 and "Faculty" in r.json()["detail"]

def test_capacity_enforced(client, faculty, admin):
    client.post("/api/requests", json=req("BIG", "2026-12-03T05:30:00Z", "2026-12-03T06:30:00Z", n=150), headers=faculty)
    rid = next(x["id"] for x in client.get("/api/requests", headers=admin).json() if x["subject"] == "BIG")
    r = client.post(f"/api/requests/{rid}/decision", json={"decision": "approve", "room_id": room_id(client, admin, "IET20")}, headers=admin)
    assert r.status_code == 400

def test_blueprint_rooms_loaded(client, admin):
    rooms = {r["name"]: r for r in client.get("/api/campus/rooms", headers=admin).json()}
    assert rooms["Library"]["floor"] == "Ground Floor" and rooms["Library"]["mapped"]
    assert rooms["LH05"]["building"] == "Deeksha Bhawan" and rooms["LH05"]["floor"] == "Ground Floor"
    assert rooms["LH13"]["floor"] == "First Floor"            # corrected from VERIFY by blueprint
    assert rooms["IET23"]["floor"] == "Second Floor"
    assert rooms["CSE Laboratory"]["floor"] == "First Floor" and not rooms["CSE Laboratory"]["mapped"]

def test_map_search_scenarios(client, admin):
    g = lambda q: client.get("/api/campus/search", params={"q": q}, headers=admin).json()["best"]
    lib = g("Central Library"); assert (lib["building"], lib["floor"], lib["name"]) == ("IET", "Ground Floor", "Library")
    lh = g("LH05"); assert (lh["building"], lh["floor"]) == ("Deeksha Bhawan", "Ground Floor")
    lab = g("CSE lab"); assert (lab["building"], lab["floor"], lab["mapped"]) == ("IET", "First Floor", False)
    assert g("Where is the Director's Office")["name"] == "Director's Office" or g("director")["name"] == "Director's Office"

def test_routes_are_flagged_approximate(client, admin):
    r = client.get("/api/campus/route", params={"to": "LH05"}, headers=admin).json()
    assert r["approximate"] and r["available"] and len(r["polyline"]) >= 2
    r = client.get("/api/campus/route", params={"to": "ECE Laboratory"}, headers=admin).json()
    assert r["available"] is False and r["polyline"] is None
    r = client.get("/api/campus/route", params={"to": "LH05", "from_building": "IET"}, headers=admin).json()
    assert r["outdoor_metres"] == 100

def test_outdoor_marked_unverified(client, student):
    o = client.get("/api/campus/outdoor", headers=student).json()
    assert o["verified"] is False and "warning" in o
