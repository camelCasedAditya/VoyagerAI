import requests
import os
from dotenv import load_dotenv

load_dotenv()

def search_yelp(term, lat, lng, radius, limit, price, time, number_of_people, date, categories=["food", "restaurants"]):
    api_key = os.getenv("YELP_API_KEY")
    url = "https://api.yelp.com/v3/businesses/search"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    query_params = {
        "latitude": f"{lat}",
        "longitude": f"{lng}",
        "term": f"{term}",
        "radius": f"{radius}",
        "categories": f"{categories}",
        "locale": "en_US",
        "price": f"{price}",
        "open_at": f"{time}",
        "sort_by": "best_match",
        "reservation_date": f"{date}",
        "reservation_time": f"{time}",
        "reservation_covers": f"{number_of_people}",
        "matches_party_size_param": None,
        "limit": 20,
        "offset": 0
    }

    response = requests.get(url, headers=headers)
    with open("yelp_response.json", "w") as f:
        f.write(response.text)

    print(response.text)
search_yelp(term="sushi", lat=37.7749, lng=-122.4194, radius=4000, limit=20, price="1,2", time="19:00", number_of_people=2, date="2023-12-31")