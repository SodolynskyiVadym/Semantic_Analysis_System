import json
import os
import time
import pika
from faster_whisper import WhisperModel
from dotenv import load_dotenv

# --- Path and variable configuration ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

load_dotenv(os.path.join(CURRENT_DIR, "config.env"))
load_dotenv(os.path.join(CURRENT_DIR, "secret.env"), override=True)

MODEL_DIR = os.path.join(CURRENT_DIR, os.getenv("MODEL_PATH", "models"))
TRANSCRIPTION_PATH = os.path.join(CURRENT_DIR, "transcription_data")

WHISPER_MODEL_SIZE = "medium"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_BEAM_SIZE = 8

# --- Model loading ---
print("Loading Whisper model into VRAM...")
model = WhisperModel(
    WHISPER_MODEL_SIZE, 
    device="cuda", 
    compute_type=WHISPER_COMPUTE_TYPE,
    download_root=MODEL_DIR
)
print("Model successfully loaded and ready for use.\n")


# --- Message processing logic ---
def process_audio_task(ch, method, properties, body):
    """
    This function is called every time RabbitMQ delivers a new task.
    """
    try:
        # 1. Parse the message
        # task_data = json.loads(body.decode("utf-8"))
        # task_id = task_data.get("task_id")
        # file_path = task_data.get("file_path") # FastAPI should pass the full/relative path
        








        task_data = json.loads(body.decode("utf-8"))
        task_id = task_data.get("task_id")
        
        # Отримуємо сирий шлях з Windows-слешами
        raw_file_path = task_data.get("file_path") 
        
        # Хитрість: замінюємо всі \ на /, а потім витягуємо ЛИШЕ назву файлу
        # Наприклад, з "uploads\123.mp4" ми отримаємо просто "123.mp4"
        filename = raw_file_path.replace('\\', '/').split('/')[-1]
        
        # Тепер безпечно будуємо правильний абсолютний шлях для Linux-контейнера
        absolute_file_path = os.path.join(CURRENT_DIR, "uploads", filename)

        print(f"\n[x] Received task {task_id}. Looking for file at: {absolute_file_path}")










        # 2. Check if the file exists
        if not os.path.exists(absolute_file_path):
            print(f"[!] Error: File \'{absolute_file_path}\' not found! Skipping...")
            # Reject the message so it doesn\'t get stuck in a loop (or basic_nack)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"[*] Starting transcription for task: {task_id}")

        
        # 3. Transcription
        segments, _ = model.transcribe(
            absolute_file_path, 
            beam_size=WHISPER_BEAM_SIZE, 
            vad_filter=True,
            vad_parameters=dict(
                threshold=0.1, # Знижуємо поріг "голосу" (стандартно 0.5). Тепер навіть тихий голос пройде.
                min_speech_duration_ms=250 # Мінімальна тривалість звуку, щоб вважати його голосом
            ),
            language="ru" # For radio intercepts
        )
        
        transcript_data = []
        full_text = ""
        
        for segment in segments:
            text = segment.text.strip()
            print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {text}")
            
            transcript_data.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": text,
                "confidence": round(1 - segment.no_speech_prob, 2)
            })
            full_text += text + " "
            
        # 4. Save the result to a file (name = task_id.json)
        os.makedirs(TRANSCRIPTION_PATH, exist_ok=True)
        output_file = os.path.join(TRANSCRIPTION_PATH, f"{task_id}.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=4)
            
        print(f"[v] Transcription saved to {output_file}")
        
        
        # 5. Tell RabbitMQ: "Task successfully completed, delete from queue"
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[!] Critical error during processing task {task_data.get('task_id', 'UNKNOWN')}: {e}")
        # If an error occurs, the file is not lost! We just don\'t send ACK,
        # and RabbitMQ will try to deliver it again or send it to the Dead Letter Queue.
        # For simplicity during development, we can nack without returning to the queue:
        # ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


# --- Connect to RabbitMQ and start the "eternal loop" ---
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
    # Retry mechanism: wait until RabbitMQ starts (important for Docker Compose)
    while not connection:
        try:
            print(f"Connecting to RabbitMQ at {rabbitmq_host}...")
            connection = pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ is not ready yet. Retrying in 5 seconds...")
            time.sleep(5)

    channel = connection.channel()
    
    # Create the queue if it doesn\'t exist
    channel.queue_declare(queue=queue_name, durable=True)
    
    # Configure QOS so that the worker takes only 1 file at a time
    channel.basic_qos(prefetch_count=1)
    
    # Subscribe to the queue
    channel.basic_consume(queue=queue_name, on_message_callback=process_audio_task)

    print(f"[*] Worker is running and waiting for messages in \'{queue_name}\'. To exit press CTRL+C")
    try:
        channel.start_consuming() # Start the eternal loop
    except KeyboardInterrupt:
        print("\nStopping worker...")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    start_worker()