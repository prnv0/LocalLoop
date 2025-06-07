import googlemaps
from dotenv import load_dotenv
from datetime import datetime
from services.geocode_services import geocode_address
from services.places_service import search_nearby_places
from services.itinerary_service import generate_itinerary
from fastapi import FastAPI, Query
import os

load_dotenv()

app = FastAPI()

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

    restaurant_places = places['restaurant_places']
    attraction_places = places['attraction_places']

    itinerary = generate_itinerary(lat, lng, restaurant_places, attraction_places)

    return {
        "hotel": hotel_info,
        "itinerary": itinerary
    }
