"""Blueprint-derived campus data.

All geometry is traced from the IET / Deeksha Bhawan blueprint in
docs/BUILD_WITH_AI_DevOps_Problem_Statement.pdf (page 1) and expressed in the
pixel space of ``frontend/public/blueprints/campus-blueprint.png`` (1342 x 895).

Honesty rules (do not weaken):
* A room is only given a ``rect`` if its label is printed on the blueprint.
* Rooms named in the written brief but NOT drawn on the blueprint (laboratories,
  faculty cabins, administrative office) have ``rect=None`` and ``mapped=False``.
  They are searchable, but the UI must say their position is unverified.
* Traced rectangles are approximate (hand-traced from a raster). Routes are
  approximate and flagged as such.
"""

BLUEPRINT_IMAGE = "/blueprints/campus-blueprint.png"
BLUEPRINT_SIZE = (1342, 895)

# (building, floor) -> viewBox crop inside the blueprint image: x, y, w, h
FLOORS = {
    ("IET", "Ground Floor"): {"view": (30, 60, 740, 250), "entrance": (393, 262), "stairs": (392, 150)},
    ("IET", "First Floor"): {"view": (30, 300, 740, 235), "entrance": None, "stairs": (395, 372)},
    ("IET", "Second Floor"): {"view": (30, 545, 740, 235), "entrance": None, "stairs": (395, 620)},
    ("Deeksha Bhawan", "Ground Floor"): {"view": (795, 75, 530, 365), "entrance": (993, 395), "stairs": (1083, 318)},
    ("Deeksha Bhawan", "First Floor"): {"view": (795, 455, 530, 300), "entrance": None, "stairs": (1081, 698)},
}

FLOOR_ORDER = {"Ground Floor": 0, "First Floor": 1, "Second Floor": 2}

# Room table.  rect = (x, y, w, h) in blueprint pixel space.
# type: classroom | lab | library | office | hall | admin
# status: DEMO (capacity is a demo estimate), VERIFY (needs confirmation)
R = []


def room(building, floor, name, rect, rtype, capacity, facilities, status, note="", aliases=()):
    R.append(dict(building=building, floor=floor, name=name, rect=rect, type=rtype,
                  capacity=capacity, facilities=facilities, status=status, note=note,
                  aliases=list(aliases), mapped=rect is not None))


# ---- IET ground floor -------------------------------------------------------
room("IET", "Ground Floor", "Library", (55, 108, 300, 64), "library", 165, "Reading,Exam", "DEMO",
     "Brief: approx. 150-180 students; sometimes used for examinations.",
     ["central library", "library"])
room("IET", "Ground Floor", "Teachers' Office", (55, 173, 300, 72), "office", 0, "", "VERIFY",
     "", ["teachers office", "staff room", "faculty office"])
room("IET", "Ground Floor", "Placement Cell", (528, 108, 202, 64), "office", 0, "", "VERIFY", "", ["placement"])
room("IET", "Ground Floor", "Director's Office", (528, 176, 202, 69), "office", 0, "", "VERIFY", "",
     ["director office", "director"])
# Named in the brief, not drawn separately on the blueprint:
room("IET", "Ground Floor", "Faculty Cabins", None, "office", 0, "", "VERIFY",
     "Listed in the brief; not drawn separately on the blueprint.", ["faculty cabin", "cabins"])
room("IET", "Ground Floor", "Administrative Office", None, "admin", 0, "", "VERIFY",
     "Listed in the brief; not labelled on the blueprint.", ["admin office", "administrative office"])

# ---- IET first floor --------------------------------------------------------
room("IET", "First Floor", "IET22", (58, 338, 137, 72), "classroom", 0, "", "VERIFY",
     "Drawn on blueprint but not in the written room list.")
room("IET", "First Floor", "IET16", (200, 338, 155, 72), "classroom", 0, "", "VERIFY",
     "Drawn on blueprint but not in the written room list.")
room("IET", "First Floor", "IET14", (433, 338, 147, 72), "classroom", 0, "", "VERIFY",
     "Drawn on blueprint but not in the written room list.")
room("IET", "First Floor", "IET15", (585, 338, 145, 72), "classroom", 0, "", "VERIFY",
     "Drawn on blueprint but not in the written room list.")
room("IET", "First Floor", "IET20", (58, 442, 167, 66), "classroom", 75, "Projector,Whiteboard", "DEMO")
room("IET", "First Floor", "IET19", (230, 442, 158, 66), "classroom", 75, "Projector,Whiteboard", "DEMO")
room("IET", "First Floor", "IET18", (393, 442, 167, 66), "classroom", 75, "Projector,Whiteboard", "DEMO")
room("IET", "First Floor", "IET17", (565, 442, 165, 66), "classroom", 75, "Projector,Whiteboard", "DEMO")
for lab in ("CSE", "ME", "ECE", "IT"):
    room("IET", "First Floor", f"{lab} Laboratory", None, "lab", 0, "", "VERIFY",
         "Brief places four laboratories on the first floor, but the blueprint does not label them. "
         "Position must be configured by an administrator.",
         [f"{lab.lower()} lab", f"{lab.lower()} laboratory", f"{lab.lower()}lab"])

# ---- IET second floor -------------------------------------------------------
room("IET", "Second Floor", "IET32", (58, 582, 297, 75), "hall", 200, "Projector,Audio", "DEMO",
     "Seminar Hall, approx. 200 students.", ["seminar hall", "seminar"])
room("IET", "Second Floor", "IET24", (440, 582, 142, 73), "classroom", 60, "Projector", "VERIFY")
room("IET", "Second Floor", "IET25", (587, 582, 143, 73), "classroom", 60, "Projector", "VERIFY")
room("IET", "Second Floor", "IET30", (58, 683, 167, 67), "classroom", 60, "Projector", "VERIFY")
room("IET", "Second Floor", "IET29", (230, 683, 158, 67), "classroom", 60, "Projector", "VERIFY")
room("IET", "Second Floor", "IET28", (393, 683, 167, 67), "classroom", 60, "Projector", "VERIFY")
room("IET", "Second Floor", "IET23", (565, 683, 165, 67), "classroom", 0, "", "VERIFY",
     "Drawn on blueprint but not in the written room list.")

# ---- Deeksha Bhawan ground floor -------------------------------------------
DB = "Deeksha Bhawan"
room(DB, "Ground Floor", "LH01", (948, 115, 267, 40), "classroom", 60, "Whiteboard", "DEMO")
room(DB, "Ground Floor", "LH02", (948, 163, 237, 34), "classroom", 60, "Whiteboard", "DEMO")
room(DB, "Ground Floor", "LH03", (945, 208, 90, 50), "classroom", 60, "Whiteboard", "DEMO")
room(DB, "Ground Floor", "LH04", (1042, 208, 93, 50), "classroom", 60, "Whiteboard", "DEMO")
room(DB, "Ground Floor", "LH05", (1215, 200, 87, 70), "classroom", 60, "Whiteboard", "DEMO")
room(DB, "Ground Floor", "LH06", (815, 300, 155, 70), "classroom", 60, "Whiteboard", "DEMO")
room(DB, "Ground Floor", "LH07", (1140, 300, 162, 70), "classroom", 60, "Whiteboard", "DEMO")
# ---- Deeksha Bhawan first floor --------------------------------------------
room(DB, "First Floor", "LH08", (948, 495, 267, 36), "classroom", 60, "Whiteboard", "DEMO")
room(DB, "First Floor", "LH09", (948, 540, 237, 35), "classroom", 60, "Whiteboard", "DEMO")
room(DB, "First Floor", "LH10", (945, 585, 90, 50), "classroom", 60, "Whiteboard", "DEMO")
room(DB, "First Floor", "LH11", (1042, 585, 93, 50), "classroom", 60, "Whiteboard", "DEMO")
room(DB, "First Floor", "LH12", (1215, 578, 87, 67), "classroom", 60, "Whiteboard", "DEMO")
room(DB, "First Floor", "LH13", (815, 672, 160, 68), "classroom", 0, "", "VERIFY",
     "Drawn on blueprint; brief only lists LH01-LH12.")
room(DB, "First Floor", "LH14", (1140, 672, 162, 68), "classroom", 0, "", "VERIFY",
     "Drawn on blueprint; brief only lists LH01-LH12.")

ROOMS = R

# Non-room blueprint features, for drawing / routing hints.
FEATURES = [
    {"building": "IET", "floor": "Ground Floor", "kind": "entrance", "label": "Entry Gate", "at": (393, 262)},
    {"building": "IET", "floor": "Ground Floor", "kind": "stairs", "label": "Stairs", "at": (392, 150)},
    {"building": "IET", "floor": "First Floor", "kind": "stairs", "label": "Stairs", "at": (395, 372)},
    {"building": "IET", "floor": "Second Floor", "kind": "stairs", "label": "Stairs", "at": (395, 620)},
    {"building": DB, "floor": "Ground Floor", "kind": "entrance", "label": "Entry Gate", "at": (993, 395)},
    {"building": DB, "floor": "Ground Floor", "kind": "stairs", "label": "Stairs", "at": (1083, 318)},
    {"building": DB, "floor": "First Floor", "kind": "stairs", "label": "Stairs", "at": (1081, 698)},
    {"building": DB, "floor": "Ground Floor", "kind": "amenity", "label": "Washroom", "at": (900, 233)},
    {"building": DB, "floor": "Ground Floor", "kind": "amenity", "label": "Drinking Water", "at": (1175, 233)},
    {"building": DB, "floor": "First Floor", "kind": "amenity", "label": "Washroom", "at": (900, 611)},
    {"building": DB, "floor": "First Floor", "kind": "amenity", "label": "Drinking Water", "at": (1175, 611)},
]

# Distance quoted by the problem statement; coordinates between buildings are NOT surveyed.
INTER_BUILDING = {"from": "IET", "to": "Deeksha Bhawan", "approx_metres": 100, "source": "Problem statement PDF, section 2B"}

# Outdoor map: no surveyed coordinates were supplied. These are admin-configurable
# placeholders centred on Gorakhpur and MUST be shown as "approximate / unverified".
OUTDOOR_DEFAULTS = {
    "centre": (26.7330, 83.4310),
    "zoom": 17,
    "verified": False,
    "points": [
        {"key": "main_gate", "name": "Main Entrance", "lat": 26.7326, "lng": 83.4300},
        {"key": "iet", "name": "IET", "lat": 26.7332, "lng": 83.4312},
        {"key": "deeksha", "name": "Deeksha Bhawan", "lat": 26.7340, "lng": 83.4318},
    ],
}


def route_in_floor(building, floor, room_rect, start):
    """Approximate polyline from ``start`` to the room centre through the corridor/stairs.

    The blueprint has no machine-readable corridor graph, so this returns a simple
    orthogonal path (start -> corridor y -> room door) and is always labelled approximate.
    """
    cx = room_rect[0] + room_rect[2] / 2
    cy = room_rect[1] + room_rect[3] / 2
    sx, sy = start
    # Pick a corridor y-level between the two room rows of the floor if one exists.
    corridor_y = {
        ("IET", "First Floor"): 426,
        ("IET", "Second Floor"): 670,
    }.get((building, floor))
    if corridor_y is None:
        return [(sx, sy), (sx, cy), (cx, cy)]
    return [(sx, sy), (sx, corridor_y), (cx, corridor_y), (cx, cy)]
