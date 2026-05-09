import json
import os
import time
import pika
from faster_whisper import WhisperModel
from dotenv import load_dotenv
from database import audio_tasks_collection

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)


load_dotenv(os.path.join(CURRENT_DIR, "config.env"))
load_dotenv(os.path.join(CURRENT_DIR, "secret.env"), override=True)


MODEL_DIR = os.path.join(CURRENT_DIR, os.getenv("MODEL_PATH", "model"))
WHISPER_MODEL_SIZE = "large-v3"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_BEAM_SIZE = 8


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASS", "password")
RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "stt_tasks")

AUDIO_DIR = os.getenv("AUDIO_DIR", "uploads")
if os.getenv("ENV", "NoEnv") == "DockerEnv":
    pass
else:
    AUDIO_DIR = os.path.join(PROJECT_ROOT, AUDIO_DIR)


print("Loading Whisper model...")
model = WhisperModel(
    WHISPER_MODEL_SIZE, 
    device="cpu", 
    compute_type=WHISPER_COMPUTE_TYPE,
    download_root=MODEL_DIR
)
print("Model successfully loaded.\n")


def save_to_db(task_id, segments_data):
    try:
        result = audio_tasks_collection.update_one(
            {"_id": task_id},
            {
                "$set": {
                    "status": "COMPLETED",
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


def process_audio_task(ch, method, properties, body):
    try:
        task_data = json.loads(body.decode("utf-8"))
        task_id = task_data.get("task_id")
        file_name = task_data.get("file_name") 

        file_path = os.path.join(f"{AUDIO_DIR}/{file_name}")

        print(f"\n[x] Received task {task_id}. File: {file_path}")

        if not os.path.exists(file_path):
            print(f"[!] Error: File '{file_path}' not found! Skipping...")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"[*] Starting transcription for task: {task_id}")
        
        segments, _ = model.transcribe(
            file_path, 
            beam_size=WHISPER_BEAM_SIZE, 
            vad_filter=True,
            vad_parameters=dict(threshold=0.1, min_speech_duration_ms=250),
            language="ru",
            condition_on_previous_text=False,
            log_progress=True   # REMOVE AFTER TESTING
        )
        
        transcript_data = []
        
        for segment in segments:
            text = segment.text.strip()
            print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {text}")
            
            transcript_data.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": text,
                "confidence": round(1 - segment.no_speech_prob, 2),
                "speaker_tag": "UNKNOWN"
            })
            
        save_to_db(task_id, transcript_data)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[!] Critical error processing task {task_data.get('task_id', 'UNKNOWN')}: {e}")


def start():
    rabbitmq_host = RABBITMQ_HOST
    rabbitmq_user = RABBITMQ_USER
    rabbitmq_pass = RABBITMQ_PASSWORD
    queue_name = RABBITMQ_QUEUE_NAME

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host, 
        credentials=credentials,
        heartbeat=600
    )

    connection = None
    while not connection:
        try:
            print(f"Connecting to RabbitMQ at {rabbitmq_host}...")
            connection = pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ is not ready yet. Retrying in 5 seconds...")
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=process_audio_task)

    print(f"[*] Worker is running and waiting for messages in '{queue_name}'. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nStopping worker...")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    start()