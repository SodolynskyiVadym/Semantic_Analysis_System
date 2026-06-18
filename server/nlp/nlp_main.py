import json
import asyncio
import sys
import aio_pika

from config import settings
from nlp.database import update as update_db, get as get_db, update_status
from nlp.models import AudioTaskUpdate, TaskStatus
from nlp.nlp import NLPProcessor 
from setup_logger import setup_worker_logger


log = setup_worker_logger("nlp_worker", settings.NLP_LOG_FILE)

try:
    log.info("Loading NER model...")
    ner_processor = NLPProcessor()
    log.info("NER model loaded successfully.")
except Exception as e:
    log.critical("Failed to load NER model: %s", str(e), exc_info=True)
    sys.exit(1)


async def process_audio_task(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        task_data = json.loads(message.body.decode("utf-8"))
        task_id = task_data.get("id")

        log.info("Received NLP task: %s", task_id)

        document = await get_db(task_id)
        if document is None:
            log.error("No suitable document found in DB for task_id: %s. Skipping...", task_id)
            return

        try:
            log.info("Starting XLM-RoBERTa NER analysis for task %s...", task_id)
            
            analysis, entities = await asyncio.to_thread(
                ner_processor.process, 
                document.transcription
            )

            if not analysis:
                log.warning("NER analysis returned empty results for task %s.", task_id)

            payload = AudioTaskUpdate(
                status=TaskStatus.COMPLETED, 
                analysis=analysis, 
                entities=entities
            )
            await update_db(task_id, payload)
            
            log.info("Task %s completed successfully. Entities saved to DB.", task_id)
            
        except Exception as e:
            log.error("Critical error during NER processing or DB update for task %s: %s", task_id, str(e), exc_info=True)
            await update_status(task_id, TaskStatus.FAILED)
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

    queue = await channel.declare_queue(settings.RABBITMQ_NLP_QUEUE, durable=True)

    log.info("Async NLP Worker is running and waiting for messages in '%s'. To exit press CTRL+C", settings.RABBITMQ_NLP_QUEUE)
    
    await queue.consume(process_audio_task)

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        log.info("Closing RabbitMQ connection...")
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())