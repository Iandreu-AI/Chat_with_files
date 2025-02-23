import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("https://api.deepseek.com/v1/")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4000))
    CONTEXT_WINDOW = int(os.getenv("CONTEXT_WINDOW", 6000))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))