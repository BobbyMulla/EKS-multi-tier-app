from flask import Flask
import requests
import os

app = Flask(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service")

@app.route("/")
def home():
    response = requests.get(BACKEND_URL)
    return f"""
    <h1>Frontend</h1>
    <p>Response from backend:</p>
    <pre>{response.text}</pre>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
