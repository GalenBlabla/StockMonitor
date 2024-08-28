from core.interfaces import Notifier
from core.events import AnalysisEvent
from typing import List
import json
import logging
from aio_pika import connect_robust, Message
from config import settings

logger = logging.getLogger(__name__)

class RabbitMQNotifier(Notifier):
    async def notify(self, stock_code: str, events: List[AnalysisEvent]):
        connection = await connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()

        # 声明队列
        await channel.declare_queue('notifications', durable=False)

        try:
            for event in events:
                message = json.dumps(event.to_dict())
                await channel.default_exchange.publish(
                    Message(body=message.encode()),
                    routing_key='notifications'
                )
                # logger.info(f"Notification sent for {stock_code}: {event.event_type}")
        finally:
            await connection.close()
