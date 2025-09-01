from flask import Flask, render_template, jsonify, request
from langchain_community.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent
import csv
import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv('openai_api_key')

app = Flask(__name__, template_folder='templates')

def load_matches():
      matches = []
      with open('matches.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                  matches.append({
                  'date': row['date'],
                  'match': row['match'],
                  'seats_available': int(row['seats_available'])
                  })
      return matches

def save_matches(matches):
      with open('matches.csv', 'w', newline='') as file:
            fieldnames = ['date', 'match', 'seats_available']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(matches)

def book_ticket(date, match, seats):
      matches = load_matches()
      for m in matches:
            if m['date'] == date and m['match'] == match:
                  if m['seats_available'] >= int(seats):
                        m['seats_available'] -= int(seats)
                        save_matches(matches)
                        return f"Successfully booked {seats} seat(s) for the match {match} on {date}."
                  else:
                        return "Not enough seats available."
      return "Match not found."

# LangChain tool for ticket booking
def ticket_booking_tool(input_str):
      try:
            input_parts = dict(part.split('=') for part in input_str.split(', '))
            date = input_parts.get('date')
            match = input_parts.get('match')
            seats = input_parts.get('seats')

            if not date or not match or not seats:
                  return "Invalid input. Provide details as: date=..., match=..., seats=..."

            return book_ticket(date, match, seats)
      except Exception as e:
            return f"Error processing booking: {str(e)}"

      
tool = Tool(
      name = "Ticket booking tool",
      description= "Book cricket match tickets. Provide input as: date=..., match=..., seats=...",
      func= ticket_booking_tool
)

llm = ChatOpenAI(model= "gpt-4", openai_api_key=OPENAI_API_KEY, temperature=0)
agent = initialize_agent(llm=llm, tools=[tool], agent = "zero-shot-react-description")

@app.route('/')
def index():
      return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask():
      data = request.json
      user_query = data.get('query', '')

      if not user_query:
            return jsonify({"error": "Query is required"}), 400

      try:
            response = agent.run(user_query)
            return jsonify({"response": response})
      except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/matches', methods=['GET'])
def get_matches():
      matches = load_matches()
      match_list = [match['match'] for match in matches]
      return jsonify({"matches": match_list})

if __name__ == '__main__':
      app.run(debug=True)