import os
from dotenv import load_dotenv
import json

load_dotenv()
class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LLM_MODEL = "llama-3.3-70b-versatile"
    APPEAL_FILE = "logs/appeals.json"
    COMMON_AI_WORD_COUNT_LIMIT = (400, 800)
    COMMON_AI_WORD_COUNT_SENTENCE = (12, 18)
    COMMON_AI_WORD_COUNT_PARAGRAPTH = (4, 6)
    RATE_LIMITING = 60


if not Config.GROQ_API_KEY:
    raise ValueError("[ERROR] API KEY was not found")


def get_appeals():
    with open(Config.APPEAL_FILE, 'r') as file:
        return json.load(file)

def save(f):
    with open(Config.APPEAL_FILE, 'w') as file:
        json.dump(f, file, indent=4)