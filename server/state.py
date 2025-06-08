# server/state.py
from typing import Dict
from uuid import uuid4

# session_id → session data
sessions: Dict[str, dict] = {}

def new_session() -> str:
    sid = str(uuid4())
    sessions[sid] = {
        "step": 0,           # which question we last asked
        "prefs": {},         # itinerary_type, food_keywords, travel_mode, max_distance_km
        "hotel": None,       # geocoded hotel info
        "places": [],        # full list from search
        "itinerary": None,   # last generated itinerary
    }
    return sid

def get_session(sid: str) -> dict:
    return sessions.get(sid)

def clear_session(sid: str):
    sessions.pop(sid, None)