from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Vasbyt bot is aan die loop!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("Incoming message:", data)

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
