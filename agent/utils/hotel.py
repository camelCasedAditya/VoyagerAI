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

# @tool("get_hotels", return_direct=True)
def get_hotels(address: str, radius: float) -> list[dict]:


    latitude, longitude = gecode_address(address)

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
            "radius": radius,
            "radiusUnit": "KM",
            "hotelSource": "ALL"
        }
    )
    ids = []
    parsed_data = parse_hotels(response.json())
    details = get_hotel_details(parsed_data, 2, "2026-05-05", "2026-05-07", 1)
    valid_ids = []
    for index, hotel_data in enumerate(list(details["data"])):
        valid_ids.append((hotel_data["hotel"]["hotelId"], index))
    final_hotels = []
    for i in valid_ids:
        for item in parsed_data:
            if item.hotel_id == i[0]:
                temp_object = item
                temp_object.price = details["data"][i[1]]["offers"][0]["price"]["total"]
                final_hotels.append(temp_object.to_json())
    return final_hotels


def parse_hotels(hotels_data):
    list_of_hotels = []

    for i in range(len(hotels_data["data"])):
        hotel_info = hotels_data["data"][i]
        hotel_id=hotel_info['hotelId']
        iata_code=hotel_info['iataCode']
        dupe_id=hotel_info['dupeId']
        chain_code=hotel_info["chainCode"]
        name=hotel_info['name']
        address=f"{', '.join(hotel_info['address']['lines'])}, {hotel_info['address']['cityName']}, {hotel_info['address']['stateCode']}, {hotel_info['address']['countryCode']}, {hotel_info['address']['postalCode']}"
        rating=None
        price=None
        latitude=hotel_info["geoCode"]["latitude"]
        longitude=hotel_info["geoCode"]["longitude"]
        city=hotel_info["address"]["cityName"]

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
print(get_hotels("1600 Amphitheatre Parkway, Mountain View, CA", 10))