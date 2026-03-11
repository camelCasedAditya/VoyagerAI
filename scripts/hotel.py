import requests
import json

from classes.hotelclass import Hotel

CLIENT_ID = "UeWgxTGaWBFrqGL7cmyfQveL511HYpNd"
CLIENT_SECRET = "17lAz6FPkr6oAzbH"

address = ""

# def amadeus_api_call(endpoint, params):
#     pass

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

def get_hotels(address):
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
            "radius": 5,
            "radiusUnit": "KM",
            "hotelSource": "ALL"
        }
    )
    with open("./scripts/hotels.json", "w") as file:
        file.write(json.dumps(response.json(), indent=4))
    return response.json()
print(get_hotels("1600 Amphitheatre Parkway, Mountain View, CA"))

# Used AI to understand JSON structure
def parse_hotels():
    with open("./scripts/hotels.json", "r") as file:
        list_of_hotels = []
        hotels_data = json.load(file)

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
info = parse_hotels()
print(info[0].name)
open("./scripts/hotels_parsed.json", "w").write(json.dumps(get_hotel_details(info, 2, "2026-05-05", "2026-05-07", 1), indent=4))
