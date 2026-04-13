import requests
import os
from dotenv import load_dotenv
import json
from langchain_core.tools import tool
load_dotenv()

@tool("search_yelp")
def search_yelp(lat: float, lng: float, radius: int, limit: int, price: str, time: str, number_of_people: int, date: str, categories=None):
    """Search for businesses on Yelp. Takes the parameters lat: float, lng: float, radius: int, limit: int, price: str (e.g., "1,2,3,4" or "1,3" with 1 being the lowest price tier and 4 being the highest), time: str (e.g., "19:00" format is HH:MM), number_of_people: int, date: str (e.g., "2023-12-31"). Returns a list of businesses that match the search criteria."""

    print(f"Called search_yelp with lat: {lat}, lng: {lng}, radius: {radius}, limit: {limit}, price: {price}, time: {time}, number_of_people: {number_of_people}, date: {date}, categories: {categories}")
    api_key = os.getenv("YELP_API_KEY")
    url = "https://api.yelp.com/v3/businesses/search"

    if categories is None:
        categories = ["food", "restaurants"]
    categories_param = ",".join(categories) if isinstance(categories, list) else categories

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    query_params = {
        "latitude": lat,
        "longitude": lng,
        "term": "food",
        "radius": radius,
        "categories": categories_param,
        "locale": "en_US",
        "price": price,
        "sort_by": "best_match",
        "reservation_date": date,
        "reservation_time": time,
        "reservation_covers": number_of_people,
        "matches_party_size_param": None,
        "limit": limit,
        "offset": 0
    }

    response = requests.get(url, headers=headers, params=query_params)
    # with open("yelp_response.json", "w") as f:
    #     f.write(json.dumps(response.json(), indent=4))

    return f"Here is a list of restaurants and food locations for the specified area: {json.dumps(response.json(), indent=4)}"
# search_yelp(term="sushi", lat=37.7749, lng=-122.4194, radius=4000, limit=20, price="1,2", time="19:00", number_of_people=2, date="2023-12-31")