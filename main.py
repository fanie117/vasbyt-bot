from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
import gspread
from datetime import datetime

app = Flask(__name__)

sessions = {}

QUESTIONS = [
    "Wat is jou naam?",
    "Wat is jou van?",
    "Wat is jou WhatsApp nommer?",
    "Wat is jou alternatiewe nommer? Tik 'nee' as jy nie een het nie.",
    "Wat is jou e-pos adres? Tik 'nee' as jy nie een het nie.",
    "In watter dorp bly jy?",
    "Wat is jou adres?",
    "Stem jy in om boodskappe te ontvang? Antwoord met Ja of Nee."
]

def get_sheet():
    creds_json = os.environ.get("GOOGLE_CREDS_JSON")
    sheet_name = os.environ.get("GOOGLE_SHEET_NAME")

    if not creds_json:
        raise Exception("GOOGLE_CREDS_JSON ontbreek.")
    if not sheet_name:
        raise Exception("GOOGLE_SHEET_NAME ontbreek.")

    creds_dict = json.loads(creds_json)
    gc = gspread.service_account_from_dict(creds_dict)
    return gc.open(sheet_name).sheet1

def save_to_google_sheet(data):
    sheet = get_sheet()
    row = [
        data.get("name", ""),
        data.get("surname", ""),
        data.get("whatsapp_number", ""),
        data.get("alternative_number", ""),
        data.get("email", ""),
        data.get("town", ""),
        data.get("address", ""),
        data.get("opt_in_status", ""),
        data.get("last_message", ""),
        data.get("last_message_date", "")
    ]
    sheet.append_row(row)

@app.route("/", methods=["GET"])
def home():
    return "Bot werk reg!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Webhook is live 👌", 200

    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "").replace("whatsapp:", "")
    incoming_lower = incoming_msg.lower()

    resp = MessagingResponse()
    msg = resp.message()

    if from_number not in sessions:
        sessions[from_number] = {
            "step": 0,
            "name": "",
            "surname": "",
            "whatsapp_number": from_number,
            "alternative_number": "",
            "email": "",
            "town": "",
            "address": "",
            "opt_in_status": "",
            "last_message": incoming_msg,
            "last_message_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        msg.body("Hallo 👋 Kom ons begin. " + QUESTIONS[0])
        return str(resp), 200, {"Content-Type": "application/xml"}

    session = sessions[from_number]
    step = session["step"]

    if step == 0:
        session["name"] = incoming_msg
        session["step"] = 1
        msg.body(QUESTIONS[1])

    elif step == 1:
        session["surname"] = incoming_msg
        session["step"] = 2
        msg.body(QUESTIONS[2])

    elif step == 2:
        session["whatsapp_number"] = incoming_msg
        session["step"] = 3
        msg.body(QUESTIONS[3])

    elif step == 3:
        session["alternative_number"] = "" if incoming_lower == "nee" else incoming_msg
        session["step"] = 4
        msg.body(QUESTIONS[4])

    elif step == 4:
        session["email"] = "" if incoming_lower == "nee" else incoming_msg
        session["step"] = 5
        msg.body(QUESTIONS[5])

    elif step == 5:
        session["town"] = incoming_msg
        session["step"] = 6
        msg.body(QUESTIONS[6])

    elif step == 6:
        session["address"] = incoming_msg
        session["step"] = 7
        msg.body(QUESTIONS[7])

    elif step == 7:
        session["opt_in_status"] = "Yes" if incoming_lower in ["ja", "yes", "y"] else "No"
        session["last_message"] = incoming_msg
        session["last_message_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            save_to_google_sheet(session)
            msg.body("Dankie 🙌 Jou besonderhede is suksesvol gestoor.")
        except Exception as e:
            print("Google Sheets error:", str(e))
            msg.body("Dankie. Jou boodskap is ontvang, maar Google Sheets is nog nie reg opgestel nie.")

        del sessions[from_number]

    else:
        sessions.pop(from_number, None)
        msg.body("Kom ons begin weer. " + QUESTIONS[0])

    return str(resp), 200, {"Content-Type": "application/xml"}
