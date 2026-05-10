import os
from pymongo import MongoClient
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(CURRENT_DIR, "config.env"))
load_dotenv(os.path.join(CURRENT_DIR, "secret.env"), override=True)

MONGO_URI = os.getenv("MONGO_CONNECTION_STRING", "mongodb://admin:password@localhost:27017/")

try:
    client = MongoClient(MONGO_URI)
    db = client["analysis_db"]
    audio_tasks_collection = db["audio_tasks"]
    print("MongoDB client and database collection initialized.")
except Exception as e:
    print(f"Error initializing MongoDB client or database: {e}")
    raise
