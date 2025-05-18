from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme için açık, istersen localhost ile sınırla
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AIRLINE_API_URL = os.getenv("AIRLINE_API_URL")
AIRLINE_USERNAME = os.getenv("AIRLINE_USERNAME")
AIRLINE_PASSWORD = os.getenv("AIRLINE_PASSWORD")

openai = OpenAI(api_key=OPENAI_API_KEY)

class ChatRequest(BaseModel):
    message: str

# Dinamik token al
async def get_airline_token():
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.post(
            f"{AIRLINE_API_URL}/Auth/login",
            json={
                "username": AIRLINE_USERNAME,
                "password": AIRLINE_PASSWORD
            }
        )
        if res.status_code == 200:
            return res.json()["token"]
        else:
            raise Exception(f"Login failed: {res.status_code} - {res.text}")

@app.post("/chat")
async def chat_with_ai(req: ChatRequest):
    user_message = req.message

    # 1. Intent extraction
    chat_response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"""
You are a strict flight assistant intent parser.

You MUST return only one of the following `intent` values:
- "QueryFlight"
- "BuyTicket"
- "CheckIn"

Return JSON only in the following formats:

# QueryFlight
{{
  "intent": "QueryFlight",
  "airportFrom": "Istanbul",
  "airportTo": "Ankara",
  "date": "2025-05-20"
}}

# BuyTicket
{{
  "intent": "BuyTicket",
  "flightId": "FL-1F0E29",
  "passengerName": "Gojo Satoru"
}}

# CheckIn
{{
  "intent": "CheckIn",
  "ticketId": "TK-8B4F21"
}}

Do NOT explain anything. Return ONLY the JSON.

### Message to parse:
"{user_message}"
"""
            }
        ]
    )

    parsed = chat_response.choices[0].message.content.strip()
    print("🔎 LLM Output:", parsed)

    try:
        intent_data = eval(parsed) if "{" in parsed else {}
    except Exception as e:
        return {"error": "LLM response is not valid JSON", "raw": parsed, "exception": str(e)}

    try:
        token = await get_airline_token()
    except Exception as e:
        return {"error": "Login to Airline API failed", "exception": str(e)}

    # ✈️ QueryFlight intent
    if intent_data.get("intent") == "QueryFlight":
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.get(
                f"{AIRLINE_API_URL}/Flight/query",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "airportFrom": intent_data["airportFrom"],
                    "airportTo": intent_data["airportTo"],
                    "date": intent_data["date"]
                }
            )
            print("✈️ QueryFlight:", res.status_code, res.text)
            try:
                return res.json()
            except Exception as e:
                return {"error": "Airline API response is not valid JSON", "status_code": res.status_code, "raw": res.text, "exception": str(e)}

    # 🎟 BuyTicket intent
    elif intent_data.get("intent") == "BuyTicket":
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.post(
                f"{AIRLINE_API_URL}/Ticket/buy",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "flightId": intent_data["flightId"],
                    "passengerName": intent_data["passengerName"]
                }
            )
            print("🎟 BuyTicket:", res.status_code, res.text)
            try:
                return res.json()
            except Exception as e:
                return {"error": "Airline API response is not valid JSON", "status_code": res.status_code, "raw": res.text, "exception": str(e)}

    # ✅ CheckIn intent
    elif intent_data.get("intent") == "CheckIn":
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.put(
                f"{AIRLINE_API_URL}/Ticket/checkin",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "ticketId": intent_data["ticketId"]
                }
            )
            print("✅ CheckIn:", res.status_code, res.text)
            try:
                return res.json()
            except Exception as e:
                return {"error": "Airline API response is not valid JSON", "status_code": res.status_code, "raw": res.text, "exception": str(e)}

    # ❌ Unknown intent
    return {"error": "Unsupported intent", "raw": intent_data}
