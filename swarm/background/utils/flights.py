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

# Function to fill in the origin and destination fields in the google flights scraper
def fill_airport_field(driver, wait, aria_label_fragment, airport_code):
    field = wait.until(EC.element_to_be_clickable(
        (By.XPATH, f"//input[contains(@aria-label, '{aria_label_fragment}')]")
    ))
    field.click()
    time.sleep(0.2)
    active = driver.switch_to.active_element
    active.send_keys(Keys.CONTROL + "a")
    active.send_keys(Keys.DELETE)
    active.send_keys(airport_code)
    time.sleep(0.2)
    active.send_keys(Keys.RETURN)
    time.sleep(0.2)

# Main function that the agent calls to scrape google flight results for the trip
@tool("scrape_flights")
def scrape_flights_ui(origin: str, destination: str, departure_date: str, return_date: str):
    """Takes the parameters origin (e.g., "PDX"), destination (e.g., "JFK"), departure_date (e.g., "05/08/2026"), and return_date (e.g., "05/30/2026"). Scrapes flight information from Google Flights and returns a list of flights that match the search criteria."""

    print(f"Called scrape_flights_ui with origin: {origin}, destination: {destination}, departure_date: {departure_date}, return_date: {return_date}")

    # Initializes selenium webdriver with headless chrome for scraper to use
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        # Navigates to Google Flights
        driver.get("https://www.google.com/travel/flights")
        time.sleep(1)

        # Input the start and end locations
        fill_airport_field(driver, wait, "Where from", origin)

        fill_airport_field(driver, wait, "Where to", destination)

        # Clicks on the departure date fields
        date_field = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[contains(@aria-label, 'Departure')]")
        ))
        driver.execute_script("arguments[0].click();", date_field)
        time.sleep(0.2)

        # Clears the departure date field and inputs the intended departure date
        date_field.send_keys(Keys.CONTROL + "a")
        date_field.send_keys(Keys.DELETE)
        date_field.send_keys(departure_date)
        time.sleep(0.2)
        date_field.send_keys(Keys.TAB)
        time.sleep(0.2)

        # Clicks on the return date field
        return_field = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@aria-label='Return']")
        ))
        driver.execute_script("arguments[0].click();", return_field)
        time.sleep(0.4)

        # Clears the return date field and inputs the intended return date
        return_field.send_keys(Keys.CONTROL + "a")
        return_field.send_keys(Keys.DELETE)
        return_field.send_keys(return_date)
        time.sleep(0.2)
        return_field.send_keys(Keys.TAB)
        time.sleep(0.2)

        # Exits the date selector through clicking the done button or escape key
        try:
            done_btn = driver.find_element(By.XPATH, "//button[.//span[text()='Done']]")
            done_btn.click()
        except Exception:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(0.4)

        # Clicks the search button to get flight results
        search_btn = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[@aria-label='Search' or .//span[text()='Search']]")
        ))
        driver.execute_script("arguments[0].click();", search_btn)

        time.sleep(0.5)

        # load_more_btn = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'View more flights')]")
        # load_more_btn[0].click()

        # time.sleep(0.5)

        # Grabs elements from search
        results = driver.find_elements(By.XPATH, "//ul[@aria-label]//li")

        flights = [el for el in results if el.text.strip() and any(
            keyword in el.text for keyword in ["$", "USD", " hr ", " min", "nonstop", "stop"]
        )]

        if not flights:
            flights = driver.find_elements(By.XPATH, "//li[.//span[contains(text(),'$')]]")

        flight_texts = []
        if not flights:
            # Failsafe to scrape all elements in HTML body
            print("Could not find structured results. Raw page sample:")
            body_text = driver.find_element(By.TAG_NAME, "body").text
            print(body_text[:3000])
        else:
            # Appends each flight info to a list
            for flight in flights:
                text = flight.text.strip()
                if text:
                    flight_texts.append(text)
                    # Print out flight info for debugging
                    print(text)
                    print("-" * 60)
    finally:
        driver.quit()
    # Token counter for debugging purposes
    tc = TokenCount("gpt-3.5-turbo")
    tokens = tc.num_tokens_from_string("\n\n".join(flight_texts))
    print(f"Token count for flight results: {tokens}")

    # Return list of flights to agent
    return f"Here is a list of flights: {flight_texts[:20]}"