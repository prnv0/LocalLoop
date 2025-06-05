import googlemaps
from dotenv import load_dotenv
from datetime import datetime
from services.geocode_services import geocode_address
from fastapi import FastAPI, Query
import os

load_dotenv()

app = FastAPI()

@app.get("/geocode")
def geocode(hotel_address: str = Query(..., description="Hotel name or address")):
    result = geocode_address(hotel_address)
    if result:
        return result
    else:
        return {"error": "Could not geocode address"}
