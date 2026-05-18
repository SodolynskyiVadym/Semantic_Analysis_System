import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "config.env")) 

MONGO_URI = os.getenv("MONGO_CONNECTION_STRING", "mongodb://admin:password@localhost:27017/")

client = MongoClient(MONGO_URI)
db = client[os.getenv("MONGO_DB_NAME", "analysis_db")]

audio_tasks_collection = db["audio_tasks"]


def save_transcription_to_db(task_id, segments_data):
    try:
        result = audio_tasks_collection.update_one(
            {"_id": task_id},
            {
                "$set": {
                    "status": "TRANSCRIBED",
                    "transcription": segments_data
                }
            }
        )
        if result.matched_count == 0:
            print(f"[!] Warning: Task {task_id} not found in MongoDB.")
        else:
            print(f"[v] Successfully saved transcription for task {task_id} to MongoDB.")
            
    except Exception as e:
        print(f"[!] Database error for task {task_id}: {e}")
        raise e