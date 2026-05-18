import json
import os
import asyncio
import aio_pika

from config import settings
from stt import run_transcription
from database import update as update_db
from models import AnalysisUpdate, AnalysisStatus


async def process_audio_task(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        task_data = json.loads(message.body.decode("utf-8"))
        task_id = task_data.get("task_id")
        file_name = task_data.get("file_name")


        file_path = os.path.join(settings.AUDIO_DIR, file_name)

        print(f"\n[x] Received task {task_id}. File: {file_path}")

        if not os.path.exists(file_path):
            print(f"[!] Error: File '{file_path}' not found! Skipping...")
            await update_db(task_id, AnalysisUpdate(status=AnalysisStatus.FAILED))
            return

        try:
            print(f"[*] Starting transcription for {task_id}...")
            
            transcript_data = await asyncio.to_thread(run_transcription, file_path)
            
            payload = AnalysisUpdate(
                status=AnalysisStatus.COMPLETED,
                transcription=transcript_data
            )
            await update_db(task_id, payload)
            
            print(f"[v] Task {task_id} completed successfully.")

        except Exception as e:
            print(f"[!] Critical error processing task {task_id}: {e}")
            await update_db(task_id, AnalysisUpdate(status=AnalysisStatus.FAILED))
            raise e 


async def main():
    connection = None
    while not connection:
        try:
            print(f"Connecting to async RabbitMQ at {settings.RABBITMQ_HOST}...")
            amqp_url = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}/"
            connection = await aio_pika.connect_robust(amqp_url)
        except Exception:
            print("RabbitMQ is not ready yet. Retrying in 5 seconds...")
            await asyncio.sleep(5)


    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    queue = await channel.declare_queue(settings.RABBITMQ_QUEUE, durable=True)

    print(f"[*] Async Worker is running and waiting for messages in '{settings.RABBITMQ_QUEUE}'. To exit press CTRL+C")
    
    await queue.consume(process_audio_task)

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        print("\nClosing connection...")
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())