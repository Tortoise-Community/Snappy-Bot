from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/health", methods=["GET", "HEAD"])
def health():
    return "Healthy!", 200

def run():
    app.run(host="0.0.0.0", port=8080)

def health_check():
    t = Thread(target=run)
    t.start()
