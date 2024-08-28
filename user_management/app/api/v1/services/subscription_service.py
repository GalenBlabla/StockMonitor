from tortoise.exceptions import DoesNotExist
from fastapi import HTTPException
from app.models.sub_models import Subscriptions
from app.api.v1.services.rabbitmq_service import send_subscription_update

async def create_subscription(user_id: int, stock_code: str):
    await Subscriptions.create(user_id=user_id, stock_code=stock_code)
    await send_subscription_update(stock_code, "subscribe")

async def delete_subscription(user_id: int, stock_code: str):
    deleted_count = await Subscriptions.filter(user_id=user_id, stock_code=stock_code).delete()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    await send_subscription_update(stock_code, "unsubscribe")

async def push_all_subscriptions_to_mq():
    # 获取所有用户的订阅
    subscriptions = await Subscriptions.all()
    
    for subscription in subscriptions:
        # 将每个订阅推送到 RabbitMQ
        await send_subscription_update(subscription.stock_code, "subscribe")
