from flask import Flask, request, jsonify
from database import missions,users
from dotenv import load_dotenv
import os
from flask_cors import CORS
load_dotenv()

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)
CORS(app)#stopts the error must be right after here

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"message": "Spy Agency API is running"})



#mission end point
@app.route("/api/missions", methods=["GET"])
def get_mission():
    return jsonify(missions)

#mission end point with id 
@app.route("/api/missions/<int:mission_id>", methods=["GET"])
def get_mission_id(mission_id):

    mission = find_mission(mission_id)

    if not mission:
        return jsonify({"error": "mission not found"}), 404

    return jsonify(mission)



#this si the function that finds the movies and thend adds it toget by id

def find_mission(mission_id):
    return next((m for m in missions if m["id"] == mission_id), None)



#login in api

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    # check if user exists with matching password
    user = next((u for u in users if u["username"] == username and u["password"] == password), None)

    if user:
        return jsonify({"api_key": API_KEY})  # ← return the key
    
    return jsonify({"error": "Invalid credentials"}), 401  # ← wrong login


# API KEY CHECK
@app.before_request
def check_api_key():
    # skip preflight CORS requests
    if request.method == "OPTIONS":
        return None
    
    
    # skip these endpoints, no key needed
    if request.path in ["/api/login", "/api/health"]:
        return None

    # get the key from the Authorization header
    key = request.headers.get("Authorization")

    if not key:
        return jsonify({"error": "API key missing"}), 401
    
    if key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401


if __name__ == "__main__":
    app.run(debug=True)

