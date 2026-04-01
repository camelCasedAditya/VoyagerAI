import os

from langchain.agents import create_agent
from langchain_cerebras import ChatCerebras
from utils.hotel import get_hotels, geocode_distance_calculator
from utils.yelp import search_yelp

api_key = os.getenv("CEREBRAS_API_KEY", "csk-t5cdem3w8w4hepvkderrd8jjf6893nnh9efmhhv8yv3fwdjd")
model_name = os.getenv("CEREBRAS_MODEL", "qwen-3-235b-a22b-instruct-2507")

llm = ChatCerebras(model=model_name, api_key=api_key)

agent = create_agent(
    llm, 
    tools=[get_hotels, geocode_distance_calculator, search_yelp],
    system_prompt="You are a helpful travel agent that finds hotels for customers. Use the get_hotels function to find hotels based on the customer's query. Use the geocode_distance_calculator function to calculate distances between the hotels and the customer's desired location. Pick the top three hotels for the customer based on pricing, location, and reputation. Then use the search_yelp tool to find restaurants near the hotels for the customer. Provide the customer with a list of the top three hotels and nearby restaurants based on their query. Always use the tools provided to you to find the best hotels and restaurants for the customer. If you don't have enough information to answer the customer's query, ask them for more information."
    )
response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Plan a trip for near 1600 Amphitheatre Parkway, Mountain View, CA for 2 adults checking in on May 5th, 2026 and checking out on May 7th, 2026. I need 1 room. Also find me the three best restaurants and food locations",
            }
        ]
    }
)
print(response["messages"][-1].content)