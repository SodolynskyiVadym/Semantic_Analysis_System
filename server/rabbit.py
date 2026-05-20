from __future__ import annotations
import json
from typing import Any
import aio_pika
import aio_pika.abc
from aio_pika import DeliveryMode, ExchangeType, Message
from server.config import settings


class RabbitClient:
    def __init__(self) -> None:
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None


    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            login=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASSWORD,
        )

        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=1)
        await self._channel.declare_queue(
            settings.RABBITMQ_STT_QUEUE,
            durable=True,
        )

        print(f"RabbitMQ connected to {settings.RABBITMQ_STT_QUEUE}")


    async def disconnect(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            print("RabbitMQ disconnected.")


    async def publish(self, message: dict[str, Any]) -> None:
        if self._channel is None or self._channel.is_closed:
            raise RuntimeError("RabbitMQ channel is not connected.")

        body = json.dumps(message, ensure_ascii=False).encode()

        await self._channel.default_exchange.publish(
            Message(
                body=body,
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
            ),
            routing_key=settings.RABBITMQ_STT_QUEUE,
        )

rabbit_client = RabbitClient()