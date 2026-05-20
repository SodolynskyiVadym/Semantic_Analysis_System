import json
import asyncio
import aio_pika
from nlp.config import settings
from nlp.database import update as update_db, get as get_db
from nlp.models import AudioTaskUpdate, TaskStatus
from nlp.nlp import run_ner


async def process_audio_task(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        task_data = json.loads(message.body.decode("utf-8"))
        id = task_data.get("id")

        document = await get_db(id)
        if document is None:
            print(f"[!] No suitable document found for task_id: {id}")
            return

        try:
            analysis, entities = await asyncio.to_thread(run_ner, document.transcription)

            payload = AudioTaskUpdate(
                status=TaskStatus.COMPLETED, 
                analysis=analysis, 
                entities=entities
            )
            await update_db(id, payload)
            
        except Exception as e:
            print(f"[!] Error updating document: {e}")
            await update_db(id, AudioTaskUpdate(status=TaskStatus.FAILED))
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