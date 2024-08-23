import json
import logging
import pika
from config import settings

logger = logging.getLogger(__name__)

market_status = {}

def market_status_callback(ch, method, properties, body):
    """处理从RabbitMQ接收的市场状态更新"""
    data = json.loads(body)
    stock_code = data['stock_code']
    is_market_open = data['is_market_open']
    market_status[stock_code] = is_market_open
    logger.info(f"接收到市场状态更新：{stock_code} - {'开放' if is_market_open else '关闭'}")

def start_rabbitmq_listener(subscribed_stocks):
    """启动RabbitMQ监听，接收订阅更新和市场状态更新"""
    def subscription_callback(ch, method, properties, body):
        data = json.loads(body)
        stock_code = data['stock_code']
        action = data['action']
        
        if action == "subscribe":
            subscribed_stocks.add(stock_code)
            logger.info(f"已订阅 {stock_code}")
        elif action == "unsubscribe":
            subscribed_stocks.discard(stock_code)
            logger.info(f"已取消订阅 {stock_code}")

    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    
    # 订阅更新的队列
    channel.queue_declare(queue='subscription_updates')
    channel.basic_consume(queue='subscription_updates', on_message_callback=subscription_callback, auto_ack=True)

    # 市场状态更新的队列
    channel.queue_declare(queue='market_status_updates')
    channel.basic_consume(queue='market_status_updates', on_message_callback=market_status_callback, auto_ack=True)

    logger.info("已连接到 RabbitMQ，等待订阅更新...")
    channel.start_consuming()
