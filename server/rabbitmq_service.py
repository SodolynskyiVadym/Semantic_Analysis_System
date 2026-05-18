import os
import json
import aio_pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASS", "password")
RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "stt_tasks")

class RabbitMQService:
    connection: aio_pika.RobustConnection = None
    channel: aio_pika.Channel = None

    @classmethod
    async def connect(cls):
        connection_url = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}/"
        
        cls.connection = await aio_pika.connect_robust(connection_url)
        cls.channel = await cls.connection.channel()
        
        await cls.channel.declare_queue(RABBITMQ_QUEUE_NAME, durable=True)
        print("RabbitMQ connected.")

    @classmethod
    async def close(cls):
        if cls.connection and not cls.connection.is_closed:
            await cls.connection.close()
            print("RabbitMQ disconnected.")

    @staticmethod
    async def publish_task(task_id: str, file_name: str):
        message_body = json.dumps({
            "task_id": task_id,
            "file_name": file_name,
            "status": "PENDING"
        }).encode('utf-8')
        
        await RabbitMQService.channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=RABBITMQ_QUEUE_NAME,
        )