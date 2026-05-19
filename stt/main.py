import json
import os
import asyncio
import aio_pika

from config import settings
from stt import run_transcription
from database import update as update_db
from models import AnalysisUpdate, AnalysisStatus


async def process_audio_task(
    message: aio_pika.abc.AbstractIncomingMessage, 
    exchange: aio_pika.abc.AbstractExchange
):
    async with message.process():
        task_data = json.loads(message.body.decode("utf-8"))
        id = task_data.get("id")
        file_name = task_data.get("file_name")

        file_path = os.path.join(settings.AUDIO_DIR, file_name)

        print(f"\n[x] Received task {id}. File: {file_path}")

        if not os.path.exists(file_path):
            print(f"[!] Error: File '{file_path}' not found! Skipping...")
            await update_db(id, AnalysisUpdate(status=AnalysisStatus.FAILED))
            return

        try:
            print(f"[*] Starting transcription for {id}...")
            
            transcript_data = await asyncio.to_thread(run_transcription, file_path)
            

            payload = AnalysisUpdate(
                status=AnalysisStatus.TRANSCRIBED,
                transcription=transcript_data
            )
            await update_db(id, payload)
            
            print(f"[v] Task {id} transcribed successfully.")
            print(f"[*] Sending task {id} to NLP queue...")

            nlp_message = json.dumps({"id": id}).encode("utf-8")
            
            await exchange.publish(
                aio_pika.Message(
                    body=nlp_message,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=settings.RABBITMQ_OUTPUT_QUEUE
            )

        except Exception as e:
            print(f"[!] Critical error processing task {id}: {e}")
            await update_db(id, AnalysisUpdate(status=AnalysisStatus.FAILED))
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

    stt_queue = await channel.declare_queue(settings.RABBITMQ_INPUT_QUEUE, durable=True)
    
    await channel.declare_queue(settings.RABBITMQ_OUTPUT_QUEUE, durable=True)
    exchange = channel.default_exchange

    print(f"[*] Async STT Worker is running and waiting for messages in '{settings.RABBITMQ_INPUT_QUEUE}'. To exit press CTRL+C")
    
    async def on_message(message: aio_pika.abc.AbstractIncomingMessage):
        await process_audio_task(message, exchange)

    await stt_queue.consume(on_message)

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        print("\nClosing connection...")
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())