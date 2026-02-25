from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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

def scrape_flights_ui(origin, destination, departure_date, return_date):
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://www.google.com/travel/flights")
        time.sleep(1)

        fill_airport_field(driver, wait, "Where from", origin)

        fill_airport_field(driver, wait, "Where to", destination)

        date_field = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[contains(@aria-label, 'Departure')]")
        ))
        driver.execute_script("arguments[0].click();", date_field)
        time.sleep(0.2)

        date_field.send_keys(Keys.CONTROL + "a")
        date_field.send_keys(Keys.DELETE)
        date_field.send_keys(departure_date)
        time.sleep(0.2)
        date_field.send_keys(Keys.TAB)
        time.sleep(0.2)

        return_field = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@aria-label='Return']")
        ))
        driver.execute_script("arguments[0].click();", return_field)
        time.sleep(0.4)

        return_field.send_keys(Keys.CONTROL + "a")
        return_field.send_keys(Keys.DELETE)
        return_field.send_keys(return_date)
        time.sleep(0.2)
        return_field.send_keys(Keys.TAB)
        time.sleep(0.2)

        try:
            done_btn = driver.find_element(By.XPATH, "//button[.//span[text()='Done']]")
            done_btn.click()
        except Exception:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(0.4)

        search_btn = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[@aria-label='Search' or .//span[text()='Search']]")
        ))
        driver.execute_script("arguments[0].click();", search_btn)

        time.sleep(0.5)

        load_more_btn = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'View more flights')]")
        load_more_btn[0].click()

        time.sleep(0.5)

        results = driver.find_elements(By.XPATH, "//ul[@aria-label]//li")

        flights = [el for el in results if el.text.strip() and any(
            keyword in el.text for keyword in ["$", "USD", " hr ", " min", "nonstop", "stop"]
        )]

        if not flights:
            flights = driver.find_elements(By.XPATH, "//li[.//span[contains(text(),'$')]]")

        if not flights:
            print("Could not find structured results. Raw page sample:")
            body_text = driver.find_element(By.TAG_NAME, "body").text
            print(body_text[:3000])
        else:
            for flight in flights:
                text = flight.text.strip().replace('\n', ' | ')
                if text:
                    print(text)
                    print("-" * 60)
    finally:
        driver.quit()

# Example usage
# start = input("Origin airport code (e.g. LAX): ")
# end = input("Destination airport code (e.g. HND): ")
# departure = input("Departure date (e.g. May 15, 2026): ")
# return_date = input("Return date (e.g. May 30, 2026): ")
# scrape_flights_ui(start, end, departure, return_date)
scrape_flights_ui("PDX", "JFK", "05/08/2026", "05/30/2026")