import os
import googlemaps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def generate_itinerary(lat, lng, restaurant_places, attraction_places):
    """
    Given a starting hotel location and a list of places, generate an itinerary using Directions API.
    """
    waypoints = []

    # Combine restaurants and attractions (limit to, e.g., top 5)
    combined_places = (restaurant_places + attraction_places)[:5]
    for place in combined_places:
        waypoints.append(f"{place['latitude']},{place['longitude']}")

    if not waypoints:
        return {"error": "No places to generate an itinerary"}

    try:
        directions_result = gmaps.directions(
            origin=f"{lat},{lng}",
            destination=f"{lat},{lng}",  # loop back to hotel
            waypoints=waypoints,
            optimize_waypoints=True,
            mode="walking"  # or "driving"
        )

        if not directions_result:
            return {"error": "No route found"}

        route = directions_result[0]
        ordered_places = []
        order = route.get('waypoint_order', list(range(len(waypoints))))

        for idx in order:
            place = combined_places[idx]
            ordered_places.append(place)

        return {
            "ordered_places": ordered_places,
            "summary": route.get('summary', ''),
            "legs": [
                {
                    "start_address": leg['start_address'],
                    "end_address": leg['end_address'],
                    "distance": leg['distance']['text'],
                    "duration": leg['duration']['text'],
                }
                for leg in route.get('legs', [])
            ]
        }

    except Exception as e:
        print(f"Error generating itinerary: {e}")
        return {"error": "Failed to generate itinerary"}