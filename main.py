from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# Onthou: hierdie werk vir eenvoudige toetsing.
# As Railway restart, verloor hy tydelike session data.
user_sessions = {}

def get_google_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]

    google_creds_json = os.environ.get("GOOGLE_CREDS_JSON")
    sheet_name = os.environ.get("GOOGLE_SHEET_NAME")

    if not google_creds_json:
        raise Exception("GOOGLE_CREDS_JSON ontbreek.")
    if not sheet_name:
        raise Exception("GOOGLE_SHEET_NAME ontbreek.")

    creds_dict = json.loads(google_creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

def save_to_sheet(data):
    sheet = get_google_sheet()
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
    return "Vasbyt bot is aan die loop!"

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    incoming_msg_lower = incoming_msg.lower()
    whatsapp_number = request.values.get("From", "").replace("whatsapp:", "")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    resp = MessagingResponse()
    msg = resp.message()

    # Begin nuwe session
    if whatsapp_number not in user_sessions:
        user_sessions[whatsapp_number] = {
            "step": "ask_name",
            "whatsapp_number": whatsapp_number,
            "last_message": incoming_msg,
            "last_message_date": now_str
        }
        msg.body("Hallo 👋 Welkom. Stuur asseblief jou naam.")
        return str(resp), 200, {"Content-Type": "application/xml"}

    session = user_sessions[whatsapp_number]
    session["last_message"] = incoming_msg
    session["last_message_date"] = now_str
    step = session.get("step")

    if step == "ask_name":
        session["name"] = incoming_msg
        session["step"] = "ask_surname"
        msg.body("Dankie. Stuur asseblief jou van.")

    elif step == "ask_surname":
        session["surname"] = incoming_msg
        session["step"] = "ask_alternative_number"
        msg.body("Stuur asseblief jou alternatiewe nommer. Tik 'nee' as jy nie een het nie.")

    elif step == "ask_alternative_number":
        session["alternative_number"] = "" if incoming_msg_lower == "nee" else incoming_msg
        session["step"] = "ask_email"
        msg.body("Stuur asseblief jou e-pos adres. Tik 'nee' as jy nie een het nie.")

    elif step == "ask_email":
        session["email"] = "" if incoming_msg_lower == "nee" else incoming_msg
        session["step"] = "ask_town"
        msg.body("Van watter dorp of area is jy?")

    elif step == "ask_town":
        session["town"] = incoming_msg
        session["step"] = "ask_address"
        msg.body("Stuur asseblief jou adres.")

    elif step == "ask_address":
        session["address"] = incoming_msg
        session["step"] = "ask_opt_in"
        msg.body("Mag ons jou in die toekoms kontak? Antwoord net met Yes of No.")

    elif step == "ask_opt_in":
        if incoming_msg_lower in ["yes", "y", "ja"]:
            session["opt_in_status"] = "Yes"
        else:
            session["opt_in_status"] = "No"

        try:
            save_to_sheet(session)
            msg.body("Dankie. Jou besonderhede is suksesvol ontvang en aangeteken.")
        except Exception as e:
            print("Google Sheets fout:", str(e))
            msg.body("Jou besonderhede is ontvang, maar daar was 'n fout met stoor na Google Sheets.")

        user_sessions.pop(whatsapp_number, None)

    else:
        user_sessions[whatsapp_number] = {
            "step": "ask_name",
            "whatsapp_number": whatsapp_number,
            "last_message": incoming_msg,
            "last_message_date": now_str
        }
        msg.body("Hallo 👋 Stuur asseblief jou naam.")

    return str(resp), 200, {"Content-Type": "application/xml"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
