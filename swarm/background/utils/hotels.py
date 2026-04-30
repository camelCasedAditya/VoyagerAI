import requests
import json
from langchain_core.tools import tool


class Hotel:
    def __init__(self, hotel_id, iata_code, dupe_id, chain_code, name, address, rating, price, latitude, longitude, city):
        self.hotel_id = hotel_id
        self.iata_code = iata_code
        self.dupe_id = dupe_id
        self.chain_code = chain_code
        self.name = name
        self.address = address
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.city = city
    def print_info(self):
        print(f"Hotel ID: {self.hotel_id}")
        print(f"IATA Code: {self.iata_code}")
        print(f"Dupe ID: {self.dupe_id}")
        print(f"Chain Code: {self.chain_code}")
        print(f"Hotel Name: {self.name}")
        print(f"Address: {self.address}")
        print(f"City: {self.city}")
        print(f"Price: {self.price}")
        print(f"Latitude: {self.latitude}")
        print(f"Longitude: {self.longitude}")
    def to_json(self):
        return {
            "hotel_id": self.hotel_id,
            "iata_code": self.iata_code,
            "dupe_id": self.dupe_id,
            "chain_code": self.chain_code,
            "name": self.name,
            "address": self.address,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "city": self.city
        }

CLIENT_ID = "UeWgxTGaWBFrqGL7cmyfQveL511HYpNd"
CLIENT_SECRET = "17lAz6FPkr6oAzbH"

address = ""

def get_hotel_details(hotel_ids, adults, check_in_date, check_out_date, room_quantity):
    auth_response = requests.post(
        "https://test.api.amadeus.com/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )
    access_token = auth_response.json()["access_token"]

    response = requests.get(
        f"https://test.api.amadeus.com/v3/shopping/hotel-offers",
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            'hotelIds': [hotel.hotel_id for hotel in hotel_ids],
            'adults': adults,
            'checkInDate': check_in_date,
            'checkOutDate': check_out_date,
            'roomQuantity': room_quantity,
            'currency': 'USD'

        }
    )
    return response.json()

def gecode_address(address):
    address = address.replace(",", "").replace(" ", "+")

    geo_code_output = requests.get(
        f"https://geocode.maps.co/search?q={address}&api_key=69afbfa01cbbb421845026vul6e8b60",
    )
    geo_data = json.loads(geo_code_output.text)[0]
    latitude = geo_data["lat"]
    longitude = geo_data["lon"]

    return latitude, longitude

@tool("get_hotels")
def get_hotels(address: str) -> list[dict]:
    """Get hotels near a given address."""

    latitude, longitude = gecode_address(address)
    print(f"Called tool with address: {address}.")
    auth_response = requests.post(
        "https://test.api.amadeus.com/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )
    access_token = auth_response.json()["access_token"]

    response = requests.get(
        "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-geocode",
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "latitude": latitude,
            "longitude": longitude,
            "radius": 10,
            "radiusUnit": "KM",
            "hotelSource": "ALL"
        }
    )
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
    ids = []
    parsed_data = parse_hotels(response.json())
    details = get_hotel_details(parsed_data, 2, "2026-07-05", "2026-07-07", 1)
    valid_ids = []
    for index, hotel_data in enumerate(list(details.get("data", []))):
        valid_ids.append((hotel_data["hotel"]["hotelId"], index))
    final_hotels = []
    for i in valid_ids:
        for item in parsed_data:
            if item.hotel_id == i[0]:
                temp_object = item
                temp_object.price = details["data"][i[1]]["offers"][0]["price"]["total"]
                final_hotels.append(temp_object.to_json())
    print(f"Found hotels: {final_hotels}")
    return f"Here is a list of hotels within a 10 km radius of {address}: \n{final_hotels}"


def parse_hotels(hotels_data):
    list_of_hotels = []
    with open("hotels_data.json", "w") as f:
        json.dump(hotels_data, f, indent=4)

    for i in range(len(hotels_data["data"])):
        hotel_info = hotels_data["data"][i]
        hotel_id = hotel_info.get("hotelId")
        iata_code = hotel_info.get("iataCode")
        dupe_id = hotel_info.get("dupeId")
        chain_code = hotel_info.get("chainCode")
        name = hotel_info.get("name", "N/A")

        address_info = hotel_info.get("address", {})
        lines = address_info.get("lines", [])
        address_parts = []
        if lines:
            address_parts.append(", ".join(lines))
        for key in ("cityName", "stateCode", "countryCode", "postalCode"):
            value = address_info.get(key)
            if value:
                address_parts.append(value)
        address = ", ".join(address_parts) if address_parts else "N/A"
        rating=None
        price=None
        geo_code = hotel_info.get("geoCode", {})
        latitude = geo_code.get("latitude")
        longitude = geo_code.get("longitude")
        city = address_info.get("cityName", "N/A")

        hotel = Hotel(
            hotel_id=hotel_id,
            iata_code=iata_code,
            dupe_id=dupe_id,
            chain_code=chain_code,
            name=name,
            address=address,
            rating=rating,
            price=price,
            latitude=latitude,
            longitude=longitude,
            city=city
        )
        list_of_hotels.append(hotel)
    return list_of_hotels

@tool("geocode_distance_calculator")
def geocode_distance_calculator(address1: str, address2: str) -> float:
    """Calculate the distance in kilometers between two addresses."""
    
    lat1, lon1 = gecode_address(address1)
    lat2, lon2 = gecode_address(address2)

    from math import radians, cos, sin, asin, sqrt

    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    print (f"Calculated distance between {address1} and {address2} is {c * r} km.")
    return c * r

import serpapi

@tool("find_hotels")
def find_hotels(address: str, check_in_date: str, check_out_date: str):
    """API TO SEARCH GOOGLE HOTELS AND TAKES IN ADDRESS PARAMERER AND HOTEL DATES"""
    print(f"Called tool with address: {address}, check-in date: {check_in_date}, and check-out date: {check_out_date}.")
    client = serpapi.Client(api_key="f7c67ca2d23762c1a7523de8d8792402ee1516b02cbd8eb525c9324fc7023c96")
    results = client.search({
    "engine": "google_hotels",
    "q": "Hotels with 5 miles of " + address,
    "check_in_date": check_in_date,
    "check_out_date": check_out_date,
    "hotel_class": "4,5"
    })
    properties = results["properties"]
    properties = properties[:5]
    properties = extract_essential_hotel_data(properties)
    properties = ultra_compress_hotel_data(properties)
    print(f"Found hotels: {properties}")
    return f"Here are some hotels near {address} from {check_in_date} to {check_out_date}: \n{properties}"


# Bottom two function written by AI to parse JSON due to tedious nature.
import json

def extract_essential_hotel_data(original_data):
    """
    Transforms the detailed hotel JSON payload into the essential schema format.
    """

    print("Extracting essential hotel data from original payload.")
    essential_data = []
    
    for hotel in original_data:
        # Safely extract rate_per_night data
        rate_info = hotel.get("rate_per_night", {})
        essential_rate = {
            "lowest": rate_info.get("lowest"),
            "extracted_lowest": rate_info.get("extracted_lowest")
        }
        
        # Safely extract image data
        essential_images = [
            {
                "thumbnail": img.get("thumbnail"),
                "original_image": img.get("original_image")
            }
            for img in hotel.get("images", [])
        ]
        
        # Build the simplified hotel object
        essential_hotel = {
            "name": hotel.get("name"),
            "description": hotel.get("description"),
            "link": hotel.get("link"),
            "gps_coordinates": hotel.get("gps_coordinates"),
            "rate_per_night": essential_rate,
            "overall_rating": hotel.get("overall_rating"),
            "reviews": hotel.get("reviews"),
            "images": essential_images,
            "amenities": hotel.get("amenities", [])
        }
        
        # Remove keys with None values to keep the output clean
        essential_hotel = {k: v for k, v in essential_hotel.items() if v is not None}
        
        essential_data.append(essential_hotel)
        
    return essential_data

def ultra_compress_hotel_data(hotel_list):
    """
    Compresses hotel data by flattening nested objects, taking only the 
    first image, and minifying keys to single characters.
    """
    compressed_data = []
    
    for hotel in hotel_list:
        # Extract the flat integer price safely
        price = None
        if "rate_per_night" in hotel:
            price = hotel["rate_per_night"].get("extracted_lowest")
            
        # Extract just the very first thumbnail URL to save space
        thumbnail = None
        if hotel.get("images") and len(hotel["images"]) > 0:
            thumbnail = hotel["images"][0].get("thumbnail")

        # Build the micro object
        micro_hotel = {
            "n": hotel.get("name"),
            "p": price,
            "r": hotel.get("overall_rating"),
            "l": hotel.get("link"),
            "t": thumbnail
        }
        
        # Drop any null values to save even more bytes
        micro_hotel = {k: v for k, v in micro_hotel.items() if v is not None}
        compressed_data.append(micro_hotel)
        
    return compressed_data