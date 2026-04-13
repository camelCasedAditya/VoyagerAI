import os

from langchain.agents import create_agent
from langchain_cerebras import ChatCerebras
from .utils.hotels import get_hotels, geocode_distance_calculator
from .utils.food import search_yelp
from .utils.flights import scrape_flights_ui
import time

def plan_trip(prompt):
    api_key = os.getenv("CEREBRAS_API_KEY", "csk-t5cdem3w8w4hepvkderrd8jjf6893nnh9efmhhv8yv3fwdjd")
    model_name = os.getenv("CEREBRAS_MODEL", "qwen-3-235b-a22b-instruct-2507")

    llm = ChatCerebras(model=model_name, api_key=api_key)

    agent = create_agent(
        llm, 
        tools=[get_hotels, geocode_distance_calculator, search_yelp, scrape_flights_ui],
        system_prompt="""
            You are a expert travel agent that helps customers find the best hotels, restaurants, and flights for their trips.

            Create a comprehensive day by day plan. This should include the flights, hotel stays, and restaurant or food locations for three meals a day. Always use the tools provided to you to find the best hotels, restaurants, and flights for the customer.

            Here are some tools you can use:
            - get_hotels(location: str, check_in: str, check_out: str, num_rooms: int) -> list: This tool takes a location (e.g., "1600 Amphitheatre Parkway, Mountain View, CA"), check-in date (e.g., "2026-05-05"), check-out date (e.g., "2026-05-07"), and number of rooms (e.g., 1) and returns a list of hotels that match the search criteria.
            - geocode_distance_calculator(origin: str, destination: str) -> float: This tool takes an origin address and a destination address and returns the distance in miles between the two locations.
            - search_yelp(lat: float, lng: float, radius: int, limit: int) -> list: This tool takes latitude and longitude coordinates, a radius in meters, and a limit on the number of results to return, and returns a list of restaurants that match the search criteria.
            - scrape_flights_ui(origin: str, destination: str, departure_date: str, return_date: str) -> list: This tool takes the parameters origin (e.g., "PDX"), destination (e.g., "JFK"), departure_date (e.g., "05/08/2026"), and return_date (e.g., "05/30/2026"). Scrapes flight information from Google Flights and returns a list of flights that match the search criteria. 

            WHEN RETURNING THE COMPREHENSIVE PLAN, ALWAYS INCLUDE THE FLIGHTS, HOTEL STAYS, AND RESTAURANT OR FOOD LOCATIONS FOR THREE MEALS A DAY. ALWAYS USE THE TOOLS PROVIDED TO YOU TO FIND THE BEST HOTELS, RESTAURANTS, AND FLIGHTS FOR THE CUSTOMER. IF YOU DON'T HAVE ENOUGH INFORMATION TO ANSWER THE CUSTOMER'S QUERY, ASK THEM FOR MORE INFORMATION. PROVIDE PRICING AND TIMING INFORMATION FOR THE FLIGHTS, HOTEL STAYS, AND RESTAURANT OR FOOD LOCATIONS. MAKE SURE TO CONSIDER THE DISTANCE BETWEEN THE HOTEL AND THE RESTAURANTS OR FOOD LOCATIONS WHEN MAKING YOUR RECOMMENDATIONS.
            """
        )

    #x = """You are a helpful travel agent that finds hotels for customers. Use the get_hotels function to find hotels based on the customer's query. Use the geocode_distance_calculator function to calculate distances between the hotels and the customer's desired location. Pick the top three hotels for the customer based on pricing, location, and reputation. Then use the search_yelp tool to find restaurants near the hotels for the customer. Provide the customer with a list of the top three hotels and nearby restaurants based on their query. Always use the tools provided to you to find the best hotels and restaurants for the customer. If you don't have enough information to answer the customer's query, ask them for more information."""
    for i in range(5):
        try:
            response = agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            )
            break
        except Exception as e:
            print(f"Error invoking agent: {e}")
            if i == 4:
                return "Sorry, there was an error processing your request. Please try again later."
            else:
                print("Retrying...")
                time.sleep(1)
        # response = agent.invoke(
        #     {
        #         "messages": [
        #             {
        #                 "role": "user",
        #                 "content": prompt
        #             }
        #         ]
        #     }
        # )
    return response["messages"][-1].content