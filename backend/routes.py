from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_login import current_user, login_required
from config import (Config, 
                    add_appeal, 
                    get_story_by_id,
                    get_users, 
                    save_user,
                    get_user, 
                    get_user_by_id,
                    add_story, 
                    get_stories_json,
                    add_to_audit_log
                    )  # should make this into a class to save my sanity

from datetime import datetime, timezone
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from guard import analyze
import random

app = Flask(__name__)
app.secret_key = "ai201"

CORS(
    app,
    origins=["http://127.0.0.1:5500"],
    supports_credentials=True
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate limit exceeded. Try again later."
    }), 429
    
@app.route("/dashboard", methods=["GET"])
def dashboard():
    stories = get_all_stories()  # assumes you already have this from add_story storage

    if not stories:
        return jsonify({
            "total_submissions": 0,
            "ai_count": 0,
            "human_count": 0,
            "uncertain_count": 0,
            "ai_ratio": 0,
            "human_ratio": 0,
            "average_confidence": 0,
            "appeal_rate": 0
        })

    total = len(stories)

    ai_count = sum(1 for s in stories if s.get("attribution") == "likely_ai")
    human_count = sum(1 for s in stories if s.get("attribution") == "likely_human")
    uncertain_count = sum(1 for s in stories if s.get("attribution") == "uncertain")

    avg_confidence = sum(s.get("confidence", 0) for s in stories) / total

    appeals = [s for s in stories if s.get("appeal_id") is not None]
    appeal_rate = len(appeals) / total if total > 0 else 0

    return jsonify({
        "total_submissions": total,

        "distribution": {
            "likely_ai": ai_count,
            "likely_human": human_count,
            "uncertain": uncertain_count
        },

        "ratios": {
            "ai_ratio": ai_count / total,
            "human_ratio": human_count / total,
            "uncertain_ratio": uncertain_count / total
        },

        "average_confidence": round(avg_confidence, 4),
        "appeal_rate": round(appeal_rate, 4)
    })

@app.route("/me", methods=['GET'])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User id not found in session"}), 401
    user, exist = get_user(user_id)
    if not exist:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "success", "user": user}), 200

@app.route("/signup", methods=["POST"])
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
    date = datetime.now(tz=timezone.utc).isoformat()
    save_user({
        "id": Id,
        "verified": False,
        "username": username,
        "joined": date,
        "stories": []
    })
    session['user_id'] = Id
    
    add_to_audit_log({
        "event": "new_user",
        "id": Id,
        "user": username,
        "timestamp": date
    })
    return jsonify({"message": f"User '{username}' created"}), 201

@app.route("/login", methods=["POST"])
def login():
    print("SESSION AFTER LOGIN:", dict(session))
    data = request.get_json()
    if not data:
        return jsonify({"error": "Data was not found during login process"}), 400
    
    username = data.get("username", "")
    if not username:
        return jsonify({"error": "Username was not provided"}), 404
    
    user, exist = get_user(username)
    if not exist:
        return jsonify({"error": "User not found in database"}), 404
    session['user_id'] = user['id']
    return jsonify({"message": f"{username} logged in, welcome back!", "user": user}), 200
    
    
@app.route("/all-stories", methods=["GET"])
def get_all_stories():
    return jsonify({"stories": get_stories()}), 200
    
    
    
@app.route("/verify", methods=["POST"])
def verify():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User id not found in session"}), 401
    user, exist = get_user(user_id)
    if not exist:
        return jsonify({"error": "User not found"}), 404
    if user['verified']:
        return jsonify({"message": f"{user['username']} is already verified", "verified": True}), 200
    
    user['verified'] = True
    save_user(user)
    add_to_audit_log({
        "event": "user_verified_toggle",
        "id": user['id'],
        "user": user['username'],
        "status": True,
        "timestamp": datetime.now(tz=timezone.utc)
    })
    return jsonify({"message": f"{user['username']} is now verified", "verified": True}), 200
    
    
@app.route("/user-stories", methods=["GET"])
def get_stories():
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    
    stories = get_stories_json()
    filtered = [s for s in stories if s.get("creator_id") == user_id]
    return jsonify({"message": "success", "stories":filtered}), 200
   
    
@app.route("/publish", methods=["POST"])
@limiter.limit("2 per minute;25 per day")
def publish():
    print("SESSION AFTER PUBLISH:", dict(session))
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
    
    tags = []
    if results['origin'] == "likely_ai" and not user['verified']:
        tags.append("ai generated content")
    if user['verified']:
        tags.append("this content is authenticated")
        
    Id = str(uuid.uuid4())
    date = datetime.now(tz=timezone.utc).isoformat()
    dt = {
        "id": Id,
        "content": text,
        "creator": user['username'],
        "creator_id": user['id'],
        "publish_date": date,
        "attribution": results['origin'],
        "confidence": results['score'],
        "status": "classified",
        "tags": tags
    }
    user['stories'].append(dt)
    save_user(user)
    add_story(dt)
    add_to_audit_log({
        "event": "story_published",
        "user": user['username'],
        "story_id": Id,
        "attribution": results['origin'],
        "confidence":results['score'],
        "timestamp": date
    })
    return jsonify({"message": f"{user['username']} published new story"}), 201
    
    
    
@app.route("/appeal", methods=["POST"])
@limiter.limit("10 per minute;100 per day") 
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
        details = "The user believes the 'AI' mark is incorrect and wants further verification."
        
    story, exist = get_story_by_id(story_id)
    if not exist:
        return jsonify({"error": "Story was not found"}), 404
    
    story['appeal_id'] = Id
    story["appeal_date"] = datetime.now(tz=timezone.utc).isoformat()
    story['details'] = details.lower().strip()
    
    add_appeal(story)
    
    # save appeal event without adding 'event' to appeal itself
    story['event'] = "appeal_submitted"
    add_to_audit_log(story)
    return jsonify({"message": f"Appeal created by the user '{story['creator']}'", "appeal": story})

    
