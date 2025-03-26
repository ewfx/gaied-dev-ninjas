import os
from dotenv import load_dotenv

load_dotenv()

def api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")    
    return api_key