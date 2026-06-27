import os
from dotenv import load_dotenv
import json

load_dotenv()
class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LLM_MODEL = "llama-3.3-70b-versatile"
    APPEAL_FILE = "logs/appeals.json"
    USERS = "logs/users.json"
    STORIES = "logs/stories.json"
    COMMON_AI_WORD_COUNT_LIMIT = (400, 800)
    COMMON_AI_WORD_COUNT_SENTENCE = (12, 18)
    COMMON_AI_WORD_COUNT_PARAGRAPTH = (4, 6)
    RATE_LIMITING = 60


if not Config.GROQ_API_KEY:
    raise ValueError("[ERROR] API KEY was not found")


def get_appeals():
    with open(Config.APPEAL_FILE, 'r') as file:
        return json.load(file)
    
def add_appeal(appeal):
    with open(Config.APPEAL_FILE, 'r') as file:
        appeals = json.load(file)
    appeals.append(appeal)
    with open(Config.APPEAL_FILE, 'w') as file:
        json.dump(appeals, file, indent=4)
    
def save_appeal(f):
    with open(Config.APPEAL_FILE, 'w') as file:
        json.dump(f, file, indent=4)
        
        
def get_users():
    with open(Config.USERS, 'r') as file:
        return json.load(file)
    
def get_user(username:str)->tuple[dict, bool]:
    if not username:
        return {}, False
    
    username = username.lower().strip()
    with open(Config.USERS, 'r') as file:
        users = json.load(file)
        
    for user in users:
        if user['username'].lower() == username:
            return user, True
        
    return {}, False

def get_user_by_id(Id:str)->tuple[dict, bool]:
    if not Id:
        return {}, False

    with open(Config.USERS, 'r') as file:
        users = json.load(file)
        
    for user in users:
        if user['id'] == Id:
            return user, True
        
    return {}, False
            

def save_user(data):
    users = get_users()
    users.append(data)
    with open(Config.USERS, 'w') as file:
        json.dump(users, file, indent=4)
        
def get_stories_json():
    with open(Config.STORIES, 'r') as file:
        return json.load(file)


def get_story_by_id(Id:str)->tuple[dict, bool]:
    if not Id:
        return {}, False

    with open(Config.STORIES, 'r') as file:
        stories = json.load(file)
        
    for story in stories:
        if story['id'] == Id:
            return story, True
        
    return {}, False
                
def add_story(dt):
    stories = get_stories_json()
    stories.append(dt)
    with open(Config.STORIES, 'w') as file:
        json.dump(stories, file, indent=4)