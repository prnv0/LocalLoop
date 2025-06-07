import os
import googlemaps
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def get_place_details(lat, lng, included_types="", max_result_count=10, radius=3000):
    """
    Find list of places near a given location.

    """
    place_details = requests.post(
        'https://places.googleapis.com/v1/places:searchNearby',
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_MAPS_API_KEY,
            'X-Goog-FieldMask': 'places.displayName,places.rating,places.location,places.formattedAddress,places.types,places.id'
        },
        json={
            "includedTypes": included_types,
            "maxResultCount": max_result_count,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": radius
                }
            }
        })
    
    # Check if the request was successful
    if place_details.status_code == 200:
        return place_details.json()
    else:
        print(f"Error: {place_details.status_code} - {place_details.text}")
        return {"results": []}


def search_nearby_places(lat, lng, radius=2000, min_rating=4.0, target_time=None):
    """
    Search for nearby restaurants and attractions within a radius (meters).
    Filters results by minimum rating.
    """
    all_places = []
    restaurant_places = []
    attraction_places = []
    # Search for restaurants
    restaurant_results = get_place_details(lat, lng, included_types=["restaurant","cafe"], max_result_count=10, radius=radius)
    restaurant_places.extend(_filter_places(restaurant_results.get('places', []), min_rating, target_time))

    # Search for tourist attractions
    attraction_results = get_place_details(lat, lng, included_types=["tourist_attraction", "museum", "park", "zoo", "amusement_park", "aquarium", "art_gallery", "bowling_alley", "casino", "church", "city_hall", "courthouse", "embassy", "hindu_temple", "library", "mosque", "museum", "night_club", "park", "zoo"], max_result_count=10, radius=radius)
    attraction_places.extend(_filter_places(attraction_results.get('places', []), min_rating, target_time))

    print(f"Found {len(restaurant_places)} restaurants and {len(attraction_places)} attractions:")
    
    return {"restaurant_places": restaurant_places, "attraction_places": attraction_places}

def _filter_places(places, min_rating, target_time=None):
    filtered = []
    for place in places:
        rating = place.get('rating', 0)
        if rating >= min_rating:
            # Check opening hours if target_time is provided
            open_now = True
            if target_time:
                opening_hours = place.get('openingHours', {}).get('periods', [])
                open_now = False  # Default to closed unless we find it open

                # Iterate through periods
                for period in opening_hours:
                    open_day = period.get('open', {}).get('day')
                    open_time_str = period.get('open', {}).get('hour', '') + period.get('open', {}).get('minute', '')
                    close_time_str = period.get('close', {}).get('hour', '') + period.get('close', {}).get('minute', '')

                    if not open_time_str or not close_time_str:
                        continue  # skip incomplete data

                    # Example: open_time_str = "0930", close_time_str = "2200"
                    try:
                        open_time = datetime.strptime(open_time_str, "%H%M").time()
                        close_time = datetime.strptime(close_time_str, "%H%M").time()
                        now_weekday = datetime.today().weekday()  # 0 = Monday, 6 = Sunday

                        if now_weekday == open_day:
                            if open_time <= target_time <= close_time:
                                open_now = True
                                break
                    except Exception as e:
                        continue

            if open_now:
                filtered.append({
                    'name': place.get('displayName', {}).get('text', ''),
                    'address': place.get('formattedAddress', ''),
                    'latitude': place.get('location', {}).get('latitude', 0),
                    'longitude': place.get('location', {}).get('longitude', 0),
                    'rating': rating,
                    'types': place.get('types', []),
                    'place_id': place.get('id', '')
                })
    return filtered