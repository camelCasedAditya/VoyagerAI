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

# Tool for agent to find hotels near a location using google maps
@tool("find_hotels")
def find_hotels(address: str) -> str:
    """Get hotels near a given address."""

    # Initialize query that will be added to url
    text = (f"Hotels near {address}").replace(" ", "+")

    url = f"https://www.google.com/maps/search/{text}/"

    # Intialize selenium browser and scraper
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Go to url with query loaded in
    driver.get(url)

    
    # Pull all hotel info which is contained in elements with role of article
    hotels = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@role='article']"))
    )
    hotel_list = []
    for i in hotels:
        hotel_list.append(i.text)
    print(f"Found {len(hotel_list)} hotels near {address}")
    tc = TokenCount("gpt-3.5-turbo")
    tokens = tc.num_tokens_from_string("\n\n".join(hotel_list))
    print(f"Token count for hotels: {tokens}")

    # Return list of hotels to the agent
    return "\n\n".join(hotel_list)
# find_hotels("cedar mill oregon")
