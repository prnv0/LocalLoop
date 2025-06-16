import os
import googlemaps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def generate_itinerary(lat, lng, places, mode="walking"):
    """
    Given a starting hotel location and places data, generate an itinerary using Directions API.
    The last stop will always be the starting location (hotel).
    """
    waypoints = []

    # Extract restaurants and attractions from places dict
    restaurant_places = places.get('restaurant_places', [])
    attraction_places = places.get('attraction_places', [])
    
    # Combine restaurants and attractions (limit to, e.g., top 5)
    combined_places = (restaurant_places + attraction_places)[:5]
    
    # Add places to waypoints
    for place in combined_places:
        waypoints.append(f"{place['latitude']},{place['longitude']}")

    if not waypoints:
        return {"error": "No places to generate an itinerary"}

    try:
        # Get directions with waypoints
        directions_result = gmaps.directions(
            origin=f"{lat},{lng}",
            destination=f"{lat},{lng}",  # loop back to hotel
            waypoints=waypoints,
            optimize_waypoints=True,
            mode=mode
        )

        if not directions_result:
            return {"error": "No route found"}

        route = directions_result[0]
        ordered_places = []
        order = route.get('waypoint_order', list(range(len(waypoints))))

        # Add places in the optimized order
        for idx in order:
            place = combined_places[idx]
            ordered_places.append(place)

        # Add the hotel as the last stop
        hotel_place = {
            'id': 'hotel',
            'name': 'Hotel',
            'address': route['legs'][-1]['end_address'],
            'latitude': lat,
            'longitude': lng,
            'rating': None
        }
        ordered_places.append(hotel_place)

        # Get legs information
        legs = []
        for i, leg in enumerate(route.get('legs', [])):
            legs.append({
                "start_address": leg['start_address'],
                "end_address": leg['end_address'],
                "distance": leg['distance']['text'],
                "duration": leg['duration']['text'],
            })

        return {
            "ordered_places": ordered_places,
            "summary": route.get('summary', ''),
            "legs": legs
        }

    except Exception as e:
        print(f"Error generating itinerary: {e}")
        return {"error": "Failed to generate itinerary"}