import json
import os
import time
import pika
from faster_whisper import WhisperModel
from dotenv import load_dotenv

# Імпорти для БД
from database import SessionLocal
from models import AudioTask, Transcription

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

load_dotenv(os.path.join(CURRENT_DIR, "config.env"))
load_dotenv(os.path.join(CURRENT_DIR, "secret.env"), override=True)

MODEL_DIR = os.path.join(CURRENT_DIR, os.getenv("MODEL_PATH", "model"))
WHISPER_MODEL_SIZE = "medium"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_BEAM_SIZE = 8

print("Loading Whisper model...")
model = WhisperModel(
    WHISPER_MODEL_SIZE, 
    device="cpu", 
    compute_type=WHISPER_COMPUTE_TYPE,
    download_root=MODEL_DIR
)
print("Model successfully loaded.\n")


def save_to_db(task_id, segments_data):
    """
    Оновлює статус завдання та створює окрему сутність Транскрипції.
    """
    with SessionLocal() as db:
        try:
            # 1. Знаходимо головне завдання
            task = db.query(AudioTask).filter(AudioTask.id == task_id).first()
            
            if not task:
                print(f"[!] Warning: Task {task_id} not found in database.")
                return

            # 2. Оновлюємо статус
            task.status = "COMPLETED"
            
            # 3. Створюємо новий запис транскрипції, прив'язаний до цього завдання
            new_transcription = Transcription(
                audio_task_id=task.id,
                segments=segments_data
            )
            
            # Додаємо транскрипцію в сесію
            db.add(new_transcription)
            
            # Зберігаємо все разом (і оновлений статус, і нову транскрипцію)
            db.commit()
            print(f"[v] Successfully saved transcription for task {task_id} to DB.")
            
        except Exception as e:
            db.rollback()
            print(f"[!] Database error for task {task_id}: {e}")
            raise e


def process_audio_task(ch, method, properties, body):
    try:
        task_data = json.loads(body.decode("utf-8"))
        task_id = task_data.get("task_id")
        
        raw_file_path = task_data.get("file_path") 
        filename = raw_file_path.replace('\\', '/').split('/')[-1]
        absolute_file_path = os.path.join(CURRENT_DIR, "uploads", filename)

        print(f"\n[x] Received task {task_id}. File: {absolute_file_path}")

        if not os.path.exists(absolute_file_path):
            print(f"[!] Error: File '{absolute_file_path}' not found! Skipping...")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"[*] Starting transcription for task: {task_id}")
        
        segments, _ = model.transcribe(
            absolute_file_path, 
            beam_size=WHISPER_BEAM_SIZE, 
            vad_filter=True,
            vad_parameters=dict(threshold=0.1, min_speech_duration_ms=250),
            language="ru"
        )
        
        transcript_data = []
        
        # Більше не збираємо full_text, тільки формуємо JSON
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
            
        # Записуємо тільки масив сегментів
        save_to_db(task_id, transcript_data)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[!] Critical error processing task {task_data.get('task_id', 'UNKNOWN')}: {e}")
        # Якщо сталася помилка БД або транскрибації - повідомлення лишається в черзі


def start_worker():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_user = os.getenv("RABBITMQ_USER", "user")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "password")
    queue_name = "stt_tasks"

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
    start_worker()