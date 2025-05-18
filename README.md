# 🧠 AI-Powered Flight Assistant - FastAPI (SE4458 Final Project)

This is a Python FastAPI project developed as a final assignment for the SE4458 Software Architecture & Design course. It connects to a RESTful Airline Ticketing API and allows users to interact using natural language, powered by OpenAI GPT-3.5.

Users can search for flights, buy tickets, and check in to their flights. The backend parses user intent from plain English and dynamically authenticates with the Airline API. A lightweight HTML/JavaScript frontend is included for testing the assistant.

---

## 🔧 Technologies Used

- Python 3.11  
- FastAPI + HTTPX  
- OpenAI GPT-3.5 API  
- Airline API (.NET 8)  
- dotenv for environment variables  
- HTML + JavaScript frontend interface  

---

## 🔐 Authentication

All requests to the Airline API require a valid token, which expires frequently. This assistant performs dynamic login using `/Auth/login` at runtime and attaches the token to all subsequent API requests. Credentials are stored in `.env`:

OPENAI_API_KEY=sk-...
AIRLINE_API_URL=https://airline-api-xxxxx.azurewebsites.net/api/v1
AIRLINE_USERNAME=admin
AIRLINE_PASSWORD=admin123


---

## 🧠 Intent Recognition with OpenAI

The assistant uses GPT-3.5 to extract structured intent from a free-form message. The supported intents are:

- `QueryFlight`  
- `BuyTicket`  
- `CheckIn`

Example message:  
"Are there flights from Istanbul to Ankara on May 20?"

Extracted JSON:
```json
{
  "intent": "QueryFlight",
  "airportFrom": "Istanbul",
  "airportTo": "Ankara",
  "date": "2025-05-20"
}

## 💬 Example Interactions

Query a flight
{
  "message": "Are there flights from Istanbul to Ankara on May 20?"
}

Buy a ticket
{
  "message": "I want to buy a ticket for flight FL-ABC123. My name is John Doe."
}

Check in
{
  "message": "I'd like to check in. My ticket ID is TK-999XYZ."
}

## ▶️ Running the Project Locally
Clone the repository
Inside the backend folder, create a .env file and configure:

OPENAI_API_KEY=sk-...
AIRLINE_API_URL=https://airline-api-xxxxx.azurewebsites.net/api/v1
AIRLINE_USERNAME=admin
AIRLINE_PASSWORD=admin123


Set up the virtual environment:

cd backend
python -m venv venv
venv\Scripts\activate  # For macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

✅ Completed Functionalities
Natural language understanding via OpenAI GPT-3.5

Dynamic login to Airline API

Querying flights

Purchasing tickets

Performing check-ins

Frontend interface for user interaction

📝 Notes
This project demonstrates how AI can be used to parse human language and integrate with microservice-based systems. It combines NLP, REST APIs, and a service-oriented backend into a unified assistant that bridges the gap between user input and business logic.