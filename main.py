from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot werk reg!"

# 👇 FIX: allow GET + POST
@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # 👉 As dit browser is (GET)
    if request.method == "GET":
        return "Webhook is live 👌", 200

    # 👉 As dit Twilio is (POST)
    incoming_msg = request.values.get("Body", "").strip()

    resp = MessagingResponse()
    msg = resp.message()
    msg.body("Ek werk nou 👌")

    return str(resp), 200, {"Content-Type": "application/xml"}
