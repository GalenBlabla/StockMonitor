# app/core/event_bus.py

from typing import Callable, Dict, List
from app.core.events import NotificationEvent
import logging
logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[NotificationEvent], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[NotificationEvent], None]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    async def publish(self, event: NotificationEvent):
        handlers = self.subscribers.get(event.event_type, [])
        for handler in handlers:
            await handler(event)

# 创建一个全局事件总线实例
event_bus = EventBus()

def event_handler(event_type: str):
    def decorator(func: Callable[[NotificationEvent], None]):
        event_bus.subscribe(event_type, func)
        return func
    return decorator
