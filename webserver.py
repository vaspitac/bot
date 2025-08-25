# webserver.py
from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def start_server():
    app.run(host="0.0.0.0", port=8080)
