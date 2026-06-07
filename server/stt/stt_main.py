import json
import os
import asyncio
import aio_pika

from config import settings
from stt.demucs import DemucsProcessor
from stt.stt import WhisperProcessor
from stt.database import update as update_db
from stt.models import AudioTaskUpdate, TaskStatus
from setup_logger import setup_worker_logger


log = setup_worker_logger("stt_worker", settings.STT_LOG_FILE)
log.info("Initializing AI models...")
demucs_processor = DemucsProcessor()
whisper_processor = WhisperProcessor()
log.info("AI models successfully loaded.")


async def process_audio_task(
    message: aio_pika.abc.AbstractIncomingMessage, 
    exchange: aio_pika.abc.AbstractExchange
):
    async with message.process():
        task_data = json.loads(message.body.decode("utf-8"))
        task_id = task_data.get("id")
        file_name = task_data.get("file_name")

        file_path = os.path.join(settings.AUDIO_DIR, file_name)

        log.info("Received task %s. Original file: %s", task_id, file_path)

        if not os.path.exists(file_path):
            log.error("File '%s' not found for task %s! Skipping...", file_path, task_id)
            await update_db(task_id, AudioTaskUpdate(status=TaskStatus.FAILED))
            return

        try:
            log.info("Starting Demucs API voice extraction for task %s...", task_id)
            
            audio_array = await asyncio.to_thread(
                demucs_processor.process, 
                file_path
            )
            
            log.info("Demucs extraction completed in memory. Starting Whisper transcription...")
            
            transcript_data = await asyncio.to_thread(
                whisper_processor.process, 
                audio_array
            )
            
            payload = AudioTaskUpdate(
                status=TaskStatus.TRANSCRIBED,
                transcription=transcript_data
            )
            await update_db(task_id, payload)

        except Exception as e:
            log.error("Critical error processing task %s: %s", task_id, str(e), exc_info=True)
            await update_db(task_id, AudioTaskUpdate(status=TaskStatus.FAILED))
            raise 


async def main():
    connection = None
    while not connection:
        try:
            log.info("Connecting to async RabbitMQ at %s...", settings.RABBITMQ_HOST)
            amqp_url = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}/"
            connection = await aio_pika.connect_robust(amqp_url)
        except Exception:
            log.warning("RabbitMQ is not ready yet. Retrying in 5 seconds...")
            await asyncio.sleep(5)

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    stt_queue = await channel.declare_queue(settings.RABBITMQ_STT_QUEUE, durable=True)
    await channel.declare_queue(settings.RABBITMQ_NLP_QUEUE, durable=True)
    exchange = channel.default_exchange

    log.info("Async STT Worker is running and waiting for messages in '%s'. To exit press CTRL+C", settings.RABBITMQ_STT_QUEUE)
    
    async def on_message(message: aio_pika.abc.AbstractIncomingMessage):
        await process_audio_task(message, exchange)

    await stt_queue.consume(on_message)

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        log.info("Closing RabbitMQ connection...")
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())