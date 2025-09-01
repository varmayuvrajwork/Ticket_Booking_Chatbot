import json
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.tools import Tool
from langchain.agents import AgentType, initialize_agent, tool
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("openai_api_key")

with open("train_data.json", "r") as file:
      train_data = json.load(file)

@tool("search_trains")
def search_trains(source: str, destination: str) -> str:
      """
      Function to search for trains between source and destination.
      Returns train details in JSON format.
      """
      results = []
      for train in train_data["trains"]:
            if source in train["route"] and destination in train["route"]:
                  # Ensure source comes before destination in route
                  if train["route"].index(source) < train["route"].index(destination):
                        results.append({
                              "train_id": train["train_id"],
                              "name": train["name"],
                              "departure": train["schedule"][source],
                              "arrival": train["schedule"][destination],
                              "seats_available": train["seats_available"],
                              "price": train["price"],
                        })
      return json.dumps(results)

llm = ChatOpenAI(model= "gpt-4", openai_api_key=OPENAI_API_KEY, temperature=0)

tools = [
      Tool(
            name="search_trains",
            func= search_trains,
            description= "Search trains from source to destination as per the user commands"
      )
]

agent = initialize_agent(
      tools=tools,
      llm=llm,
      agent= AgentType.OPENAI_FUNCTIONS,
      verbose = True
)

def chatbot():
      print("Train Booking Chatbot (type 'exit' to quit)")
      while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                  break
            user_input = user_input.lower().strip()
            if "from" in user_input and "to" in user_input:
                  try:
                        _, rest = user_input.split("from")
                        source, destination = rest.split("to")
                        source = source.strip()  
                        destination = destination.strip()  
                        if source and destination:
                              response = agent.invoke("search_trains", {"input": {"source": source, "destination": destination}})
                              print(f"Raw response from agent: {response}")
                              if response:
                                    print(f"Bot: {response}")
                              else:
                                    print("No details found for the specified route. Please try another query.")
                        else:
                              print("It seems there was an error parsing your input. Please ensure to format your request as 'From [source] to [destination]'.")
                  except Exception as e:
                        print(f"Error: {e}")
            else:
                  print("Please specify both 'from' and 'to' in your request. Example: 'From City A to City B'.")



if __name__ == '__main__':
      chatbot()