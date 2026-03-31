from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Vasbyt bot is aan die loop!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Webhook is live", 200

    incoming_msg = request.values.get("Body", "").strip()
    print("WEBHOOK HIT")
    print("Message:", incoming_msg)
    print("From:", request.values.get("From", ""))

    resp = MessagingResponse()
    msg = resp.message("Hallo 👋 Ek werk nou.")

    return str(resp), 200, {"Content-Type": "application/xml"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
