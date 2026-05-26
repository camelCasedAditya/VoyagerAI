import os
import json
import time
from cerebras.cloud.sdk import Cerebras
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from langchain_core.tools import tool
from token_count import TokenCount

# Tool for the agent to use to find best food places near a location
@tool("find_food_places")
def find_food_places(address: str) -> str:
    """Get food places near a given address."""

    # Put query into format so it can be searches through the url
    text = (f"food near {address}").replace(" ", "+")

    url = f"https://www.google.com/maps/search/{text}/"

    query = f"food near {address}"

    # Initialize selenium browser and scraper
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # wait = WebDriverWait(driver, 20)

    # Go to the url with the query loaded in
    driver.get(url)

    # Grab all elements with role of article which is the element containing restaurant details
    food = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@role='article']"))
    )

    # Array to store food place info
    food_list = []

    # Convert the elements to a python list
    for i in food:
        food_list.append(i.text)
    print(f"Found {len(food_list)} food places near {address}")
    tc = TokenCount("gpt-3.5-turbo")
    tokens = tc.num_tokens_from_string("\n\n".join(food_list))
    print(f"Token count for food places: {tokens}")

    # Return the food places to the agent
    return "\n\n".join(food_list)
# find_food_places("cedar mill oregon")