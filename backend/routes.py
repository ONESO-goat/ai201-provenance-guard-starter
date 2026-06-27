from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_login import current_user, login_required
from config import Config, save_appeal, get_appeals, add_appeal, get_story_by_id, get_users, save_user, get_user, get_user_by_id, add_story # should be making this a class
from datetime import datetime, timezone
import uuid
from guard import analyze
import random

app = Flask(__name__)

CORS(app)

app.route("/signup", options=["POST"])
def make_account():
    data = request.get_json()
    if not data:
        return jsonify({"error":"Data was not found during publish process"}), 404
    username = data.get("username","")
    if not username:
        return jsonify({"error": "Username was not provided"}), 400
    # no need for password for the quick implementation
    
    for user in get_users():
        if user['username'] == username:
            return jsonify({"error": f"The username '({username})' already being used"}), 403
    Id = str(uuid.uuid4())
    save_user({
        "id": Id,
        "username": username,
        "joined": datetime.now(tz=timezone.utc),
        "stories": []
    })
    session['user_id'] = Id
    return jsonify({"message": f"User '{username}' created"}), 201

app.route("/login", options=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Data was not found during login process"}), 400
    
    username = data.get("username", "")
    if not username:
        return jsonify({"error": "Username was not provided"}), 404
    
    user, exist = get_user(username)
    if not exist:
        return jsonify({"error": "User not found in database"}), 404
    return jsonify({"message": f"{username} logged in, welcome back!", "user": user}), 200
    
    
    
    
    
app.route("/all-stories", options=["GET"])
def get_stories():
    return jsonify({"message": "success", "stories": get_stories()}), 200
   
    
app.route("/publish", options=["POST"])
def publish():
    data = request.get_json()
    if not data:
        return jsonify({"error":"Data was not found during publish process"}), 404
    
    user, exist = get_user_by_id(session["user_id"])
    if not exist:
        return jsonify({"error": "User was not found inside the system"}), 404
    
    text = data.get("text", "")
    if not text:
        return jsonify({"error":"Data was not found during publish process"}), 404
    
    results = analyze(text)
    if not results:
        return jsonify({"error": "Error occurred during story publishing"}), 500
    
#      "content_id": "3f7a2b1e-...",
#   "creator_id": "test-user-1",
#   "timestamp": "2025-04-01T14:32:10.123Z",
#   "attribution": "likely_ai",
#   "confidence": 0.78,
#   "llm_score": 0.81,
#   "status": "classified"
    tags = []
    if results['origin'] == "likely_ai":
        tags.append("ai generate content")
    dt = {
        "id": str(uuid.uuid4()),
        "content": text,
        "creator": user['username'],
        "crator_id": user['id'],
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "attribution": results['origin'],
        "confidence": results['score'],
        "status": "classified",
        "tags": tags
    }
    user['stories'].append(dt)
    save_user(user)
    add_story(dt)
    return jsonify({"message": f"{user['username']} published new story"}), 201
    
    
    
app.route("/appeal", options=["POST"])
def submit_appeal():
    data = request.get_json()
    if not data:
        return jsonify({"error":"Data was not found during publish process"}), 404
    
    Id = random.randint(1000000000, 9999999999)
    
    story_id = data.get("story_id", "")
    details = data.get("details", "")
    if not story_id:
        return jsonify({"error": "Story id was not provided"}), 404
    if not details:
        details = "No details provided by the user"
        
    story, exist = get_story_by_id(story_id)
    if not exist:
        return jsonify({"error": "Story was not found"}), 404
    
    story['appeal_id'] = Id
    story["appeal_date"] = datetime.now(tz=timezone.utc).isoformat()
    story['details'] = details.lower().strip()
    
    add_appeal(story)
    return jsonify({"message": f"Appeal created by the user '{story['creator']}'", "appeal": story})

    
