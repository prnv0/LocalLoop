import os
import googlemaps
import requests
from datetime import datetime
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def get_place_details(lat, lng, included_types="", max_result_count=10, radius=3000):
    """
    Find list of places near a given location.

    """
    print(f"Calling Google Places API with types: {included_types}, radius: {radius}")
    
    place_details = requests.post(
        'https://places.googleapis.com/v1/places:searchNearby',
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_MAPS_API_KEY,
            'X-Goog-FieldMask': 'places.displayName,places.rating,places.location,places.formattedAddress,places.types,places.id,places.regularOpeningHours'
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
    
    print(f"API response status: {place_details.status_code}")
    
    # Check if the request was successful
    if place_details.status_code == 200:
        response_data = place_details.json()
        print(f"API response data keys: {response_data.keys()}")
        if 'places' in response_data:
            print(f"Found {len(response_data['places'])} places in API response")
        return response_data
    else:
        print(f"Error: {place_details.status_code} - {place_details.text}")
        return {"results": []}


def search_nearby_places(lat, lng, place_types=None, keywords=None, radius=5000, min_rating=3.0, target_time=None, max_results=10):
    """
    Search for nearby restaurants and attractions within a radius (meters).
    Filters results by minimum rating.
    Args:
        lat: Latitude
        lng: Longitude
        place_types: List of place types to search for
        keywords: List of keywords to filter by
        radius: Search radius in meters
        min_rating: Minimum rating to include
        target_time: Target time to check if places are open
        max_results: Maximum number of results to return per type
    """
    print(f"Searching places at lat={lat}, lng={lng}, radius={radius}, min_rating={min_rating}")
    print(f"Place types: {place_types}, Keywords: {keywords}")
    
    restaurant_places = []
    attraction_places = []

    # Determine restaurant types (use provided place_types or default to restaurant & cafe)
    rest_types = place_types if place_types else ["restaurant", "cafe"]
    print(f"Using restaurant types: {rest_types}")
    
    restaurant_results = get_place_details(lat, lng, included_types=rest_types, max_result_count=10, radius=radius)
    print(f"Raw restaurant results: {len(restaurant_results.get('places', []))} places found")
    
    restaurant_places = _filter_places(restaurant_results.get('places', []), min_rating, target_time)
    print(f"Filtered restaurant places: {len(restaurant_places)}")

    # If keywords provided, filter restaurants by keywords in name or types
    if keywords:
        print(f"Filtering by keywords: {keywords}")
        filtered = []
        for place in restaurant_places:
            name = place.get('name', '').lower()
            types = [t.lower() for t in place.get('types', [])]
            # Print debug info for first few places
            if len(filtered) < 3:
                print(f"Place: {name}, Types: {types}")
            
            # Check if any keyword matches (more flexible matching)
            match_found = False
            for kw in keywords:
                kw_lower = kw.lower()
                # Check name contains keyword or keyword contains name parts
                if (kw_lower in name or 
                    any(kw_lower in t for t in types) or
                    any(part in kw_lower for part in name.split() if len(part) > 2)):
                    filtered.append(place)
                    match_found = True
                    break
            
            # If no keywords provided or it's a generic restaurant, include it
            if not match_found and not keywords:
                filtered.append(place)
                
        restaurant_places = filtered
        print(f"After keyword filtering: {len(restaurant_places)} restaurants")

    # If no custom place_types provided, fetch attractions
    if not place_types:
        attraction_types = [
            "tourist_attraction", "museum", "park", "zoo", "amusement_park", "aquarium",
            "art_gallery", "bowling_alley", "casino", "church", "city_hall", "courthouse",
            "embassy", "hindu_temple", "library", "mosque", "night_club"
        ]
        print(f"Fetching attractions with types: {attraction_types}")
        attraction_results = get_place_details(lat, lng, included_types=attraction_types, max_result_count=10, radius=radius)
        print(f"Raw attraction results: {len(attraction_results.get('places', []))} places found")
        attraction_places = _filter_places(attraction_results.get('places', []), min_rating, target_time)
        print(f"Filtered attraction places: {len(attraction_places)}")

    print(f"Found {len(restaurant_places)} restaurants and {len(attraction_places)} attractions:")
    return {"restaurant_places": restaurant_places, "attraction_places": attraction_places}



def get_available_cuisines(lat, lng, radius=5000):
    """
    Collect all unique restaurant types from the area as cuisine options.
    """
    # Fetch nearby restaurants
    resp = gmaps.places_nearby(
        location=(lat, lng),
        radius=radius,
        type="restaurant"
    )
    results = resp.get("results", [])
    print(f"Found {len(results)} restaurants for cuisine detection")
    
    all_types = set()
    
    # Only filter out the most basic generic types
    exclude_types = {
        'establishment', 'point_of_interest', 'food', 'restaurant'
    }
    
    for place in results:
        name = place.get('name', '')
        place_types = place.get('types', [])
        
        print(f"Restaurant: '{name}' -> Types: {place_types}")
        
        # Collect all types except the most generic ones
        for place_type in place_types:
            if place_type not in exclude_types:
                all_types.add(place_type)
    
    print(f"All unique types found: {sorted(all_types)}")
    
    # Convert to readable format
    cuisine_options = []
    for place_type in sorted(all_types):
        # Convert underscores to spaces and title case
        readable = place_type.replace('_', ' ').title()
        cuisine_options.append(readable)
    
    print(f"Final cuisine options: {cuisine_options}")
    
    # If no types found, provide fallback
    if not cuisine_options:
        cuisine_options = ['Any Restaurant']
    
    return cuisine_options

def _filter_places(places, min_rating, target_time=None):
    filtered = []
    for place in places:
        rating = place.get('rating', 0)
        if rating >= min_rating:
            # Check opening hours if target_time is provided
            open_now = True
            if target_time:
                # Get opening hours from the new API format
                opening_hours_info = place.get('regularOpeningHours', {})
                periods = opening_hours_info.get('periods', [])
                open_now = False  # Default to closed unless we find it open

                # Get current day of week (Google uses 0=Sunday, 1=Monday, etc.)
                current_weekday = (datetime.now().weekday() + 1) % 7  # Convert to Google's format

                # Check if open at target_time
                for period in periods:
                    open_info = period.get('open', {})
                    close_info = period.get('close', {})
                    
                    open_day = open_info.get('day')
                    open_hour = open_info.get('hour', 0)
                    open_minute = open_info.get('minute', 0)
                    
                    if close_info:  # Some places might be open 24/7
                        close_hour = close_info.get('hour', 23)
                        close_minute = close_info.get('minute', 59)
                    else:
                        close_hour = 23
                        close_minute = 59

                    if open_day == current_weekday:
                        # Convert to minutes for easier comparison
                        target_minutes = target_time.hour * 60 + target_time.minute
                        open_minutes = open_hour * 60 + open_minute
                        close_minutes = close_hour * 60 + close_minute
                        
                        # Handle case where closing time is next day (e.g., open until 2 AM)
                        if close_minutes < open_minutes:
                            if target_minutes >= open_minutes or target_minutes <= close_minutes:
                                open_now = True
                                break
                        else:
                            if open_minutes <= target_minutes <= close_minutes:
                                open_now = True
                                break

            if open_now:
                filtered.append({
                    'id': place.get('id', ''),
                    'place_id': place.get('id', ''),
                    'name': place.get('displayName', {}).get('text', ''),
                    'address': place.get('formattedAddress', ''),
                    'latitude': place.get('location', {}).get('latitude', 0),
                    'longitude': place.get('location', {}).get('longitude', 0),
                    'lat': place.get('location', {}).get('latitude', 0),
                    'lng': place.get('location', {}).get('longitude', 0),
                    'rating': rating,
                    'types': place.get('types', [])
                })
    return filtered