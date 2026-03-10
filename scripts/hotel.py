import requests
import json

CLIENT_ID = "UeWgxTGaWBFrqGL7cmyfQveL511HYpNd"
CLIENT_SECRET = "17lAz6FPkr6oAzbH"

address = "13350 NW Manzoni St, Portland, Oregon 97229"

address = address.replace(",", "").replace(" ", "+")

geo_code_output = requests.get(
    f"https://geocode.maps.co/search?q={address}&api_key=69afbfa01cbbb421845026vul6e8b60",
)

print(geo_code_output.json())

geo_data = json.loads(geo_code_output.text)[0]
latitude  = geo_data["lat"]
longitude = geo_data["lon"]

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
print(response.json())