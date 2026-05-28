import os
import json
from dotenv import load_dotenv
import requests
from langchain_core.tools import tool


load_dotenv()


GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("GOOGLE_API_KEY")


def _geocode(address: str, api_key: str):
    params = {"address": address, "key": api_key}
    resp = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results") or []
    if not results:
        return None
    loc = results[0].get("geometry", {}).get("location")
    if not loc:
        return None
    return loc.get("lat"), loc.get("lng")


@tool("find_food_places")
def find_food_places(address: str) -> str:
    """Minimal restaurant lookup: geocode the address and run a nearby search.

    Returns a plain-text list (one entry per line) similar to the original Selenium scraper.
    """

    if not GOOGLE_PLACES_API_KEY:
        return "GOOGLE_PLACES_API_KEY not configured"

    # support passing lat,lng directly
    lat = lng = None
    if isinstance(address, str) and "," in address:
        parts = [p.strip() for p in address.split(",")]
        if len(parts) >= 2:
            try:
                lat = float(parts[0]); lng = float(parts[1])
            except Exception:
                lat = lng = None

    if lat is None or lng is None:
        geo = _geocode(address, GOOGLE_PLACES_API_KEY)
        if not geo:
            return ""
        lat, lng = geo

    params = {
        "location": f"{lat},{lng}",
        "radius": 5000,
        "type": "restaurant",
        "key": GOOGLE_PLACES_API_KEY,
    }
    resp = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json", params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    entries = []
    for place in data.get("results", []) or []:
        name = place.get("name")
        vicinity = place.get("vicinity") or place.get("formatted_address")
        rating = place.get("rating")
        parts = [p for p in [name, vicinity, f"rating:{rating}" if rating is not None else None] if p]
        entries.append(" - ".join(parts))

    return "\n\n".join(entries)

