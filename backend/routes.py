from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config, save, get_appeals
from agent import Agent

app = Flask(__name__)

CORS(app)



app.route("/publish", options=["GET"])
def get_stories():
    data = request.get_json()
    if not data:
        return jsonify({"error":"Data was not found during publish process"}), 404
    
    text = data.get("text", "")
    if not text:
        return jsonify({"error":"Data was not found during publish process"}), 404
    
    # TODO: AI LOGIC
    
app.route("/publish", options=["POST"])
def publish():
    data = request.get_json()
    if not data:
        return jsonify({"error":"Data was not found during publish process"}), 404
    
    text = data.get("text", "")
    if not text:
        return jsonify({"error":"Data was not found during publish process"}), 404
    
    # TODO: AI LOGIC
    
    
    
app.route("/appeal", options=["POST"])
def submit_appeal():
    data = request.get_json()
    if not data:
        return jsonify({"error":"Data was not found during publish process"}), 404
    
    orifinal_text = data.get("text", "")
    ai_result = data.get("origin", "")
    
    
    if not text:
        return jsonify({"error":"Data was not found during publish process"}), 404
    
    # TODO: AI LOGIC
    
    
    
