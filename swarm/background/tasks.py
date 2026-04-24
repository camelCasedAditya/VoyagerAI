from django.conf import settings
from django.core.mail import send_mail
from swarm import celery_app
import time
import requests
import os


@celery_app.task()
def delay_print():
    print("START")
    time.sleep(10)
    url = 'http://127.0.0.1:8000/background/callback/'
    myobj = {'somekey': 'somevalue'}

    headers = {'X-CSRFToken': 'bypass'}
    x = requests.post(url, json=myobj, timeout=10, headers=headers)
    
    print("This is a delayed print task.")

from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware, ModelRetryMiddleware
from langchain_cerebras import ChatCerebras
from .utils.hotels import get_hotels, geocode_distance_calculator
from .utils.food import search_yelp
from .utils.flights import scrape_flights_ui
from celery import shared_task
from travel.models import Trip
from langchain_core.tools import tool

@tool("send_update")
def send_update(text):
    """SENDS AN PROGRESS UPDATE TO THE FRONTEND. TAKES ONE PARARMETER, text, WHICH IS THE UPDATE TO SEND TO THE FRONTEND. RETURNS THE STATUS CODE OF THE POST REQUEST TO THE FRONTEND."""

    url = 'http://localhost:8000/api/print_post/'
    myobj = {'update': text}
    headers = {'X-CSRFToken': 'bypass'}
    x = requests.post(url, json=myobj, timeout=10, headers=headers)
    return x.status_code


@celery_app.task()
def plan_trip(prompt, trip_id):
    trip = Trip.objects.get(id=trip_id)
    api_key = os.getenv("CEREBRAS_API_KEY", "csk-t5cdem3w8w4hepvkderrd8jjf6893nnh9efmhhv8yv3fwdjd")
    model_name = os.getenv("CEREBRAS_MODEL", "qwen-3-235b-a22b-instruct-2507")

    llm = ChatCerebras(model=model_name, api_key=api_key)

    retry_middleware = ToolRetryMiddleware(max_retries=8, tools=[get_hotels, geocode_distance_calculator, search_yelp, scrape_flights_ui], backoff_factor=2, initial_delay=1, max_delay=30)
    model_retry_middleware = ModelRetryMiddleware(max_retries=8, backoff_factor=2, initial_delay=1, max_delay=30)

    agent = create_agent(
        llm, 
        tools=[get_hotels, geocode_distance_calculator, search_yelp, scrape_flights_ui, send_update],
        middleware=[retry_middleware, model_retry_middleware],
        system_prompt="""
            You are a expert travel agent that helps customers find the best hotels, restaurants, and flights for their trips.

            Create a comprehensive day by day plan. This should include the flights, hotel stays, and restaurant or food locations for three meals a day. Always use the tools provided to you to find the best hotels, restaurants, and flights for the customer.

            Here are some tools you can use:
            - get_hotels(location: str, check_in: str, check_out: str, num_rooms: int) -> list: This tool takes a location (e.g., "1600 Amphitheatre Parkway, Mountain View, CA"), check-in date (e.g., "2026-05-05"), check-out date (e.g., "2026-05-07"), and number of rooms (e.g., 1) and returns a list of hotels that match the search criteria.
            - geocode_distance_calculator(origin: str, destination: str) -> float: This tool takes an origin address and a destination address and returns the distance in miles between the two locations.
            - search_yelp(lat: float, lng: float, radius: int, limit: int) -> list: This tool takes latitude and longitude coordinates, a radius in meters, and a limit on the number of results to return, and returns a list of restaurants that match the search criteria.
            - scrape_flights_ui(origin: str, destination: str, departure_date: str, return_date: str) -> list: This tool takes the parameters origin (e.g., "PDX"), destination (e.g., "JFK"), departure_date (e.g., "05/08/2026"), and return_date (e.g., "05/30/2026"). Scrapes flight information from Google Flights and returns a list of flights that match the search criteria. 

            WHEN RETURNING THE COMPREHENSIVE PLAN, ALWAYS INCLUDE THE FLIGHTS, HOTEL STAYS, AND RESTAURANT OR FOOD LOCATIONS FOR THREE MEALS A DAY. ALWAYS USE THE TOOLS PROVIDED TO YOU TO FIND THE BEST HOTELS, RESTAURANTS, AND FLIGHTS FOR THE CUSTOMER. IF YOU DON'T HAVE ENOUGH INFORMATION TO ANSWER THE CUSTOMER'S QUERY, ASK THEM FOR MORE INFORMATION. PROVIDE PRICING AND TIMING INFORMATION FOR THE FLIGHTS, HOTEL STAYS, AND RESTAURANT OR FOOD LOCATIONS. MAKE SURE TO CONSIDER THE DISTANCE BETWEEN THE HOTEL AND THE RESTAURANTS OR FOOD LOCATIONS WHEN MAKING YOUR RECOMMENDATIONS.

            SEND FREQUENT UPDATES TO THE FRONTEND USING THE send_update TOOL TO LET THE CUSTOMER KNOW HOW THE PLANNING IS GOING AND WHAT STEPS YOU ARE TAKING TO PLAN THEIR TRIP.
            """
        )

    #x = """You are a helpful travel agent that finds hotels for customers. Use the get_hotels function to find hotels based on the customer's query. Use the geocode_distance_calculator function to calculate distances between the hotels and the customer's desired location. Pick the top three hotels for the customer based on pricing, location, and reputation. Then use the search_yelp tool to find restaurants near the hotels for the customer. Provide the customer with a list of the top three hotels and nearby restaurants based on their query. Always use the tools provided to you to find the best hotels and restaurants for the customer. If you don't have enough information to answer the customer's query, ask them for more information."""
    
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

    trip.result = response["messages"][-1].content
    trip.save(update_fields=['result'])

    return response["messages"][-1].content