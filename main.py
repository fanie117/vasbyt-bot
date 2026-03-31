from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
import gspread
from datetime import datetime

app = Flask(__name__)

# --- Google Sheets Setup ---
creds_json = os.environ.get("GOOGLE_CREDS_JSON")
creds_dict = json.loads(creds_json)

gc = gspread.service_account_from_dict(creds_dict)
sheet = gc.open(os.environ.get("GOOGLE_SHEET_NAME")).sheet1

# --- In-memory session storage ---
sessions = {}

questions = [
    "Wat is jou naam?",
    "Wat is jou van?",
    "Wat is jou WhatsApp nommer?",
    "Alternatiewe nommer?",
    "Email adres?",
    "In watter dorp bly jy?",
    "Wat is jou adres?",
    "Stem jy in om boodskappe te ontvang? (Ja/Nee)"
]

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From")

    resp = MessagingResponse()
    msg = resp.message()

    # New user
    if from_number not in sessions:
        sessions[from_number] = {
            "step": 0,
            "data": []
        }
        msg.body("Hallo 👋 Kom ons begin. " + questions[0])
        return str(resp)

    session = sessions[from_number]

    # Save answer
    session["data"].append(incoming_msg)
    session["step"] += 1

    # Ask next question
    if session["step"] < len(questions):
        msg.body(questions[session["step"]])
    else:
        # Save to Google Sheets
        data = session["data"]

        row = [
            data[0],  # Name
            data[1],  # Surname
            data[2],  # WhatsApp Number
            data[3],  # Alternative Number
            data[4],  # Email
            data[5],  # Town
            data[6],  # Address
            data[7],  # OptInStatus
            incoming_msg,  # Last Message
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Date
        ]

        sheet.append_row(row)

        msg.body("Dankie 🙌 Jou besonderhede is gestoor!")

        # Reset session
        del sessions[from_number]

    return str(resp)

@app.route("/")
def home():
    return "Vasbyt bot is aan die loop!"

# --- IMPORTANT FOR RAILWAY ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
