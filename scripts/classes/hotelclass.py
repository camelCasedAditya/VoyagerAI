class Hotel:
    def __init__(self, hotel_id, iata_code, dupe_id, chain_code, name, address, rating, price, latitude, longitude, city):
        self.hotel_id = hotel_id
        self.iata_code = iata_code
        self.dupe_id = dupe_id
        self.chain_code = chain_code
        self.name = name
        self.address = address
        self.rating = rating
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
        print(f"Rating: {self.rating}")
        print(f"Price: {self.price}")