import os
import googlemaps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def geocode_address(address):
    """
    Takes an address string and returns lat/lng and place_id.
    """
    try:
        geocode_result = gmaps.geocode(address)
        if not geocode_result:
            return None  # No results found

        location = geocode_result[0]['geometry']['location']
        place_id = geocode_result[0]['place_id']
        formatted_address = geocode_result[0]['formatted_address']

        return {
            'formatted_address': formatted_address,
            'latitude': location['lat'],
            'longitude': location['lng'],
            'place_id': place_id
        }
    except Exception as e:
        print(f"Error in geocoding: {e}")
        return None