import requests
import os
from dotenv import load_dotenv
import json
load_dotenv()

def search_yelp(term, lat, lng, radius, limit, price, time, number_of_people, date, categories=None):
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
        "term": f"{term}",
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
    with open("yelp_response.json", "w") as f:
        f.write(json.dumps(response.json(), indent=4))

    print(response.text)
search_yelp(term="sushi", lat=37.7749, lng=-122.4194, radius=4000, limit=20, price="1,2", time="19:00", number_of_people=2, date="2023-12-31")