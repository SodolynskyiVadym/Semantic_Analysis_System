import json
import os
import time
import pika
from dotenv import load_dotenv

from stt import run_transcription
from database import save_transcription_to_db


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

load_dotenv(os.path.join(CURRENT_DIR, "config.env"))
load_dotenv(os.path.join(CURRENT_DIR, "secret.env"), override=True)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASS", "password")
RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "stt_tasks")

AUDIO_DIR = os.getenv("AUDIO_DIR", "uploads")
if os.getenv("ENV", "NoEnv") != "DockerEnv":
    AUDIO_DIR = os.path.join(PROJECT_ROOT, AUDIO_DIR)


def process_audio_task(ch, method, properties, body):
    try:
        task_data = json.loads(body.decode("utf-8"))
        task_id = task_data.get("task_id")
        file_name = task_data.get("file_name") 

        file_path = os.path.join(AUDIO_DIR, file_name)

        print(f"\n[x] Received task {task_id}. File: {file_path}")

        if not os.path.exists(file_path):
            print(f"[!] Error: File '{file_path}' not found! Skipping...")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        transcript_data = run_transcription(file_path)
        save_transcription_to_db(task_id, transcript_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[!] Critical error processing task {task_data.get('task_id', 'UNKNOWN')}: {e}")


def start():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST, 
        credentials=credentials,
        heartbeat=600
    )

    connection = None
    while not connection:
        try:
            print(f"Connecting to RabbitMQ at {RABBITMQ_HOST}...")
            connection = pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ is not ready yet. Retrying in 5 seconds...")
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBITMQ_QUEUE_NAME, on_message_callback=process_audio_task)

    print(f"[*] Worker is running and waiting for messages in '{RABBITMQ_QUEUE_NAME}'. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nStopping worker...")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    start()