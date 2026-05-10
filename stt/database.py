import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "config.env")) 

MONGO_URI = os.getenv("MONGO_CONNECTION_STRING", "mongodb://admin:password@localhost:27017/")

client = MongoClient(MONGO_URI)
db = client[os.getenv("MONGO_DB_NAME", "analysis_db")]

audio_tasks_collection = db["audio_tasks"]