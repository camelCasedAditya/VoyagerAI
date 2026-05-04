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

def google_maps_food_search(address):

    text = (f"food near {address}").replace(" ", "+")

    url = f"https://www.google.com/maps/search/{text}/"

    query = f"food near {address}"

    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    driver.get(url)

    food = driver.find_elements(By.XPATH, "//div[@role='article']/div")
    print(food)
    for i in food:
        print(i.text)
google_maps_food_search("cedar mill oregon")