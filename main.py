from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route('/')
def home():
    return "Vasbyt bot is aan die loop!"

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    if "hi" in incoming_msg or "hello" in incoming_msg:
        msg.body("Hallo 👋 Welkom by Vasbyt Smousery! 🍑🥫")

    elif "price" in incoming_msg or "prys" in incoming_msg:
        msg.body("Ons pryse:\n- 3kg blikke: R540 per boks\n- Delivery ingesluit 🚚")

    elif "order" in incoming_msg or "koop" in incoming_msg:
        msg.body("Stuur asseblief:\nNaam\nDorp\nHoeveel bokse\nOns sal jou order bevestig ✅")

    else:
        msg.body("Dankie vir jou boodskap 🙌 Ons sal jou nou help!")

    return str(resp)

if __name__ == '__main__':
    app.run()
