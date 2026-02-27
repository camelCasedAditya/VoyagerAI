import os
import json
import time
from cerebras.cloud.sdk import Cerebras
from .scrapeflightai import scrape_flight_info

MODEL_ID = "gpt-oss-120b"

client = Cerebras(
    api_key="csk-t5cdem3w8w4hepvkderrd8jjf6893nnh9efmhhv8yv3fwdjd",
)

user_prompt = "Find me a flight from Los Angeles to New York departing on May fifth 2026 and returning on May 20th, 2026."
system_prompt = """ You are a travel agent for finding flights. You know every airport code and can find the best flights for your customers.
    
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
        {"role": "system", "content": system_prompt},
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
print(content["start_airport_code"])
flights = scrape_flight_info(start_airport_code, end_airport_code, departure_date, return_date)