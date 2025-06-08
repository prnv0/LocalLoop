# Map each itinerary_type string to the list of Google Places place types you want to query
ITINERARY_TYPE_MAP = {
    "activities":       ["bowling_alley", "amusement_park", "park","cultural_landmark"],
    "tourist":          ["tourist_attraction", "museum", "historical_place", "cultural_landmark","art_gallery","historical_landmark"],
    "foodie":           ["restaurant", "cafe", "bar"],
    "custom":           []  # you’ll fill this from explicit food_keywords etc.
}

CUISINES = ["italian","chinese","japanese","mexican","indian","thai","french","spanish","korean"]