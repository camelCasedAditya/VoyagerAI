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

    # flights = [el for el in results if el.text.strip() and any(
    #     keyword in el.text for keyword in ["$", "USD", " hr ", " min", "nonstop", "stop"]
    # )]
    
    # if not flights:
    options = []
    flights = driver.find_elements(By.XPATH, "//li[.//span[contains(text(),'$')]]")
    print(type(flights), len(flights), "candidates found with fallback method.")
    for i, flight in enumerate(flights):
        text = flight.text.strip().replace('\n', ' | ').replace('\u202f', ' ')
        if text:
            options.append(text)
    print("Quitting driver and returning results.")
    driver.quit()
    return options
        
        
        
    

MODEL_ID = "gpt-oss-120b"

client = Cerebras(
    api_key="csk-t5cdem3w8w4hepvkderrd8jjf6893nnh9efmhhv8yv3fwdjd",
)

user_prompt = "Find me a flight from Los Angeles to New York departing on May fifth 2026 and returning on May 20th, 2026."
search_system_prompt = """ You are a travel agent for finding flights. You know every airport code and can find the best flights for your customers.
    
    Output strictly VALID JSON with this schema:
    {
        "start_airport_code": "Airport Code in format (\"LAX\")",
        "end_airport_code": "Airport Code in format (\"JFK\")",
        "departure_date": "Date in format (\"05/08/2026\")",
        "return_date": "Date in format (\"05/30/2026\")",
    }"""

response = client.chat.completions.create(
    model=MODEL_ID,
    messages=[
        {"role": "system", "content": search_system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    response_format={"type": "json_object"},
    temperature=0.7
)
        
content = json.loads(response.choices[0].message.content)
print(content)
start_airport_code = content["start_airport_code"]
end_airport_code = content["end_airport_code"]
departure_date = content["departure_date"]
return_date = content["return_date"]
flights = scrape_flights_ui(start_airport_code, end_airport_code, departure_date, return_date)
text = ""
for flight in flights:
    text += flight + "\n"

pick_flight_system_prompt = """ You are a travel agent for finding flights. You can pick the best flights for your customers. Prioratize speed, airline quality, and MOST IMPRORTANTLY PRICE.
    
    PICK THE TEN BEST FLIGHT OPTIONS FOR THE USER BASED ON THE FOLLOWING RAW FLIGHT OPTION TEXTS I GOT FROM GOOGLE FLIGHTS. EACH OPTION INCLUDES AIRLINE(S), DEPARTURE AND ARRIVAL TIMES, NUMBER OF STOPS AND DURATION, AND PRICE. SOME OPTIONS MAY BE NONSTOP WHILE OTHERS MAY HAVE ONE OR MORE STOPS. SOME OPTIONS MAY BE CHEAPER BUT TAKE MUCH LONGER, WHILE OTHERS MAY BE MORE EXPENSIVE BUT FASTER. I WANT YOU TO CONSIDER ALL THESE FACTORS AND PICK THE BEST 10 OPTIONS FOR ME.

    USE THE FOLLOWING LIST AS REFERENCE FOR AIRLINE QUALITY (FROM BEST TO WORST):
    QATAR AIRWAYS
    SINGAPORE AIRLINES
    CATHAY PACIFIC AIRWAYS
    EMIRATES
    ANA ALL NIPPON AIRWAYS
    TURKISH AIRLINES
    KOREAN AIR
    AIR FRANCE
    JAPAN AIRLINES
    HAINAN AIRLINES
    SWISS INTERNATIONAL AIR LINES
    EVA AIR
    BRITISH AIRWAYS
    QANTAS AIRWAYS
    LUFTHANSA
    VIRGIN ATLANTIC
    SAUDIA
    STARLUX AIRLINES
    AIR CANADA
    IBERIA
    ETIHAD AIRWAYS
    VISTARA
    FIJI AIRWAYS
    CHINA SOUTHERN AIRLINES
    FINNAIR
    CHINA EASTERN AIRLINES
    AIR NEW ZEALAND
    DELTA AIR LINES
    AIR CHINA
    ALASKA AIRLINES
    GARUDA INDONESIA
    VIETNAM AIRLINES
    KLM ROYAL DUTCH AIRLINES
    AUSTRIAN AIRLINES
    THAI AIRWAYS
    AIRASIA
    QATAR AIRWAYS (REGIONAL)
    JETBLUE AIRWAYS
    BANGKOK AIRWAYS
    UNITED AIRLINES
    AMERICAN AIRLINES
    OMAN AIR
    GULF AIR
    ROYAL MAROC
    ETHIOPIAN AIRLINES
    TURKISH AIRLINES (REGIONAL)
    RYANAIR
    SOUTHWEST AIRLINES
    SCOOT
    INDIGO
    MALAYSIA AIRLINES
    TAP AIR PORTUGAL
    SAS SCANDINAVIAN
    BRUSSELS AIRLINES
    LOT POLISH AIRLINES
    AEGEAN AIRLINES
    AIRASTANA
    AIR TRANSAT
    WESTJET
    AZUL BRAZILIAN
    AVIANCA
    LATAM
    AEROMEXICO
    ROYAL JORDANIAN
    KUWAIT AIRWAYS
    EL AL
    PHILIPPINES AIRLINES
    HONG KONG AIRLINES
    SHENZHEN AIRLINES
    XIAMEN AIRLINES
    SICHUAN AIRLINES
    JUNEYAO AIR
    SPRING AIRLINES
    AIRASIA X
    CEBU PACIFIC
    PEGASUS AIRLINES
    FLYDUBAI
    EUROWINGS
    VUELING AIRLINES
    EASYJET
    JETSTAR AIRWAYS
    AIRBALTIC
    NORWEGIAN
    TRANSAVIA
    VOLOTEA
    ITA AIRWAYS
    ICELANDAIR
    PORTER AIRLINES
    HAWAIIAN AIRLINES
    ALLEGIANT AIR
    SPIRIT AIRLINES
    FRONTIER AIRLINES
    JETSMART
    GOL LINHAS AEREA
    KENYA AIRWAYS
    ROYAL BRUNEI AIRLINES
    AIR MAURITIUS
    RWANDAIR
    FIJI LINK
    TUI AIRWAYS

    ORDER THE FLIGHT OPTIONS IN THE JSON OUTPUT BASED ON THE CRITERIA I GAVE YOU, WITH THE BEST OPTION FIRST AND THE WORST OPTION LAST. MAKE SURE TO CONSIDER ALL FACTORS INCLUDING PRICE, DURATION, AIRLINE QUALITY, AND NUMBER OF STOPS. IF THERE ARE TIES IN YOUR RANKING, ORDER THOSE TIED OPTIONS BY PRICE, WITH CHEAPER OPTIONS FIRST. PICK OPTIONS WITH AIRLINES EXCLUSIVELY MENTIONED IN THIS LIST AS HIGHER QUALITY THAN AIRLINES NOT MENTIONED IN THIS LIST. ALSO PICK NONSTOP OPTIONS AS BETTER THAN OPTIONS WITH STOPS.
    Output strictly VALID JSON with this schema:
    [{
        "start_airport_code": "Airport Code in format (\"LAX\")",
        "end_airport_code": "Airport Code in format (\"JFK\")",
        "departure_time": "Time in 24-hour format (\"HH:MM\")",
        "arrival_time": "Time in 24-hour format (\"HH:MM\")",
        "airlines": JSON array of airline names in format [\"Delta\", \"United\"]. If multiple airlines are listed for a flight, split them into an array here.",
        "stops": "Array of stopover airport codes in format [\"ORD\", \"ATL\"]. If nonstop, return an empty array []",
        "price": "Price in USD as a number (\"350\")",
        "flight_duration": "Duration in format (\"Xhr-Ymin\")"
    }]"""    
user_prompt = f"""Here are the flight options I found for a trip from {start_airport_code} to {end_airport_code} departing on {departure_date} and returning on {return_date}:

{text}
Pick the best flight option based on the criteria I gave you and return it in the JSON format I specified."""
response = client.chat.completions.create(
    model=MODEL_ID,
    messages=[
        {"role": "system", "content": pick_flight_system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    response_format={"type": "json_object"},
    temperature=0.7
)
print(response.choices[0].message.content)