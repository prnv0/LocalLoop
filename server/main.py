import os
import googlemaps
import re
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from datetime import datetime
from services.geocode_services import geocode_address
from services.places_service import search_nearby_places, get_available_cuisines
from services.itinerary_service import generate_itinerary
from state import new_session, get_session, clear_session
from schemas import ChatRequest, ChatResponse
from config import ITINERARY_TYPE_MAP


load_dotenv()

app = FastAPI()

def _regenerate(session):
    return generate_itinerary(
        session["hotel"]["latitude"],
        session["hotel"]["longitude"],
        session["places"],
        mode=session["prefs"]["travel_mode"]
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 1. Initialize session
    if not req.session_id:
        sid = new_session()
        return ChatResponse(
            session_id=sid,
            reply="Welcome! What type of itinerary would you like? (activities / tourist / foodie / custom)",
            options=["activities", "tourist", "foodie", "custom"]
        )

    sid = req.session_id
    session = get_session(sid)
    if not session:
        raise HTTPException(400, "Invalid session_id")

    # Wrap conversation handling to catch errors and preserve session state
    try:
        text = req.message.strip().lower()

        # 2. Universal commands
        if text in {"show itinerary", "view itinerary"}:
            if session["itinerary"]:
                return ChatResponse(
                    session_id=sid,
                    reply="Here's your current itinerary:",
                    itinerary=session["itinerary"]
                )
            return ChatResponse(session_id=sid, reply="No itinerary yet. Let's finish setup first.")

        if text in {"start over", "reset"}:
            clear_session(sid)
            sid = new_session()
            return ChatResponse(session_id=sid, reply="Alright, let's start again. What type of itinerary?")

        # 3. Step-by-step preference collection
        step = session["step"]

        # Step 0: itinerary_type
        if step == 0:
            valid = {"activities", "tourist", "foodie", "custom"}
            if text not in valid:
                return ChatResponse(
                    session_id=sid,
                    reply="Please choose: activities / tourist / foodie / custom",
                    options=list(valid)
                )
            session["prefs"]["itinerary_type"] = text
            session["step"] = 1
            return ChatResponse(
                session_id=sid,
                reply="Which mode of travel? (walking / driving / transit / bicycling)",
                options=["walking", "driving", "transit", "bicycling"]
            )

        # Step 1: travel_mode
        if step == 1:
            valid_modes = {"walking", "driving", "transit", "bicycling"}
            if text not in valid_modes:
                return ChatResponse(
                    session_id=sid,
                    reply="Please pick one: walking, driving, transit, or bicycling.",
                    options=list(valid_modes)
                )
            session["prefs"]["travel_mode"] = text
            session["step"] = 2
            return ChatResponse(session_id=sid,
                                reply="Max distance from hotel in km? (e.g. 2)")

        # Step 2: max_distance_km
        if step == 2:
            try:
                dist = float(text)
            except ValueError:
                return ChatResponse(session_id=sid,
                                    reply="Give a numeric value, e.g. 2.5")
            session["prefs"]["max_distance_km"] = dist
            session["step"] = 3
            return ChatResponse(session_id=sid,
                                reply="Please tell me your hotel name or address.")

        # Step 3: hotel_address → geocode → probe cuisines
        if step == 3:
            hotel_info = geocode_address(req.message)
            if not hotel_info:
                return ChatResponse(session_id=sid,
                                    reply="Could not geocode that. Try another address.")
            session["hotel"] = hotel_info

            # probe available cuisines
            radius_m = int(session["prefs"]["max_distance_km"] * 1000)
            options = get_available_cuisines(
                hotel_info["latitude"],
                hotel_info["longitude"],
                radius=radius_m
            )

            session["prefs"]["available_cuisines"] = options
            session["step"] = 4

            return ChatResponse(
                session_id=sid,
                reply=(
                    "Great! Here are the cuisine types I found nearby:\n"
                    f"{', '.join(options)}\n\n"
                    "Which of these would you like? (You can pick multiple, comma-separated, or say 'none'.)"
                ),
                options=options
            )

        # Step 4: cuisine selection → final itinerary generation
        if step == 4:
            # parse user's choice
            text_input = text.strip().lower()
            # handle 'none' selection
            if text_input == 'none':
                chosen = []
            else:
                sel = [c.strip().lower() for c in text.split(",") if c.strip()]
                valid = [c.lower() for c in session["prefs"]["available_cuisines"]]
                chosen = [c for c in sel if c in valid]
                # if no valid cuisines chosen, ask again and don't advance step
                if not chosen:
                    return ChatResponse(
                        session_id=sid,
                        reply=(
                            "Please choose valid cuisine(s) from this list: "
                            f"{', '.join(session['prefs']['available_cuisines'])}, or say 'none'."
                        )
                    )
            session["prefs"]["food_keywords"] = chosen

            # now collect places and build itinerary
            hotel = session["hotel"]
            radius_m = int(session["prefs"]["max_distance_km"] * 1000)

            # 1) search places
            # If food keywords are chosen, search for restaurants with those keywords
            # Otherwise use the itinerary type mapping
            if session["prefs"]["food_keywords"]:
                # Search for restaurants with the selected cuisine keywords
                places = search_nearby_places(
                    hotel["latitude"],
                    hotel["longitude"],
                    place_types=None,  # Let it default to restaurants
                    keywords=session["prefs"]["food_keywords"],
                    radius=radius_m
                )
            else:
                # Use itinerary type mapping (for non-food focused itineraries)
                place_types = ITINERARY_TYPE_MAP[session["prefs"]["itinerary_type"]]
                places = search_nearby_places(
                    hotel["latitude"],
                    hotel["longitude"],
                    place_types=place_types,
                    keywords=None,
                    radius=radius_m
                )
            session["places"] = places

            # 2) generate route
            itinerary = generate_itinerary(
                hotel["latitude"],
                hotel["longitude"],
                places,
                mode=session["prefs"]["travel_mode"]
            )
            session["itinerary"] = itinerary
            session["step"] = 5  # now in "post-itinerary" mode

            return ChatResponse(
                session_id=sid,
                reply="Here's your initial itinerary:",
                itinerary=itinerary
            )

        # 4. Post-itinerary intent handlers (remove/add/change)
        if session["step"] >= 5:
            # ... your existing remove/add/change blocks here, then regenerate and return ...
            text = req.message.strip().lower()

            # 1) Show itinerary
            if text in {"show itinerary", "view itinerary"}:
                return ChatResponse(
                    session_id=sid,
                    reply="Here's your current itinerary:",
                    itinerary=session["itinerary"]
                )

            # 2) Remove Nth stop
            m = re.match(r"remove (\d+)(?:st|nd|rd|th) stop", text)
            if m:
                idx = int(m.group(1)) - 1
                if 0 <= idx < len(session["places"]):
                    session["places"].pop(idx)
                    session["itinerary"] = _regenerate(session)
                    return ChatResponse(
                        session_id=sid,
                        reply=f"Removed stop #{idx+1}. Here's the updated route:",
                        itinerary=session["itinerary"]
                    )

            # 3) Add more of a category
            m = re.match(r"add more (\w+)", text)
            if m:
                category = m.group(1)
                new_places = search_nearby_places(
                    session["hotel"]["latitude"],
                    session["hotel"]["longitude"],
                    place_types=[category],
                    keywords=session["prefs"]["food_keywords"],
                    radius=int(session["prefs"]["max_distance_km"] * 1000)
                )
                session["places"].extend(new_places)
                session["itinerary"] = _regenerate(session)
                return ChatResponse(
                    session_id=sid,
                    reply=f"Added more {category}. Here's your revised itinerary:",
                    itinerary=session["itinerary"]
                )

            # 4) Change travel mode
            if text.startswith("let's ") and " instead" in text:
                new_mode = text.split()[1]
                session["prefs"]["travel_mode"] = new_mode
                session["itinerary"] = _regenerate(session)
                return ChatResponse(
                    session_id=sid,
                    reply=f"Switched to {new_mode}. Here's your new route:",
                    itinerary=session["itinerary"]
                )

    except Exception as e:
        # Log the error and return a friendly fallback without resetting session
        print(f"Error in chat endpoint: {e}")
        return ChatResponse(
            session_id=sid,
            reply="Sorry, something went wrong. Let's try again."
        )

    # Default fallback if no branch is matched within try
    return ChatResponse(session_id=sid, reply="I didn't understand that. You can 'show itinerary' or 'reset', or finish setup first.")

@app.get("/geocode")
def geocode(hotel_address: str = Query(..., description="Hotel name or address")):
    result = geocode_address(hotel_address)
    print(result)
    if result:
        return result
    else:
        return {"error": "Could not geocode address"}
    
@app.get("/places")
def get_nearby_places(hotel_address: str, time_str: str = Query(None, description="Time in HH:MM (24-hour format)")):
    hotel_info = geocode_address(hotel_address)
    if not hotel_info:
        return {"error": "Could not geocode address"}

    lat = hotel_info['latitude']
    lng = hotel_info['longitude']

    # Parse the time string if provided
    target_time = None
    if time_str:
        try:
            target_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return {"error": "Invalid time format. Use HH:MM, e.g., 14:30."}

    places = search_nearby_places(lat, lng, target_time=target_time)

    return {"hotel": hotel_info, "places": places}

@app.get("/itinerary")
def get_itinerary(hotel_address: str):
    hotel_info = geocode_address(hotel_address)
    if not hotel_info:
        return {"error": "Could not geocode address"}

    lat = hotel_info['latitude']
    lng = hotel_info['longitude']
    places = search_nearby_places(lat, lng)

    itinerary = generate_itinerary(lat, lng, places, mode="walking")

    return {
        "hotel": hotel_info,
        "itinerary": itinerary
    }
