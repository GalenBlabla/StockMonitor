import httpx
import json
import logging
import asyncio
import pika
from datetime import datetime, time
from config import settings

logger = logging.getLogger(__name__)

market_status = {}

async def fetch_stock_data(stock_code: str):
    """从API获取股票数据"""
    try:
        params = {
            "code": stock_code,
            "all": "1",
            "isIndex": "false",
            "isBk": "false",
            "isBlock": "false",
            "stockType": "ab",
            "group": "quotation_minute_ab",
            "finClientType": "pc",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.API_STOCK_INFO, headers=settings.HEADERS, params=params)
            response.raise_for_status()
            logging.info(response.url)
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"获取股票 {stock_code} 数据时出错: {e}")
        return None

def send_to_processor(stock_code: str, data: dict):
    """将股票数据发送到 Stock Processor 服务"""
    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue='stock_data')

        message = json.dumps({
            'stock_code': stock_code,
            'data': data
        })

        channel.basic_publish(exchange='',
                              routing_key='stock_data',
                              body=message)
        logger.info(f"已将 {stock_code} 的数据发送到 Stock Processor 服务")
    except Exception as e:
        logger.error(f"发送数据到处理服务失败: {e}")
    finally:
        connection.close()

async def periodic_stock_fetch(subscribed_stocks):
    """每3秒获取一次所有订阅股票的最新数据"""
    while True:
        if subscribed_stocks:
            for stock_code in subscribed_stocks:
                # 检查市场是否开放
                logger.info(f"检查市场开放信息{market_status.get(stock_code)}")
                if market_status.get(stock_code, True):
                    data = await fetch_stock_data(stock_code)
                    if data:
                        send_to_processor(stock_code, data)
                else:
                    logger.info(f"{stock_code} 市场已关闭，跳过数据获取。")
        else:
            logger.info("没有订阅的股票，无需获取数据。")
        await asyncio.sleep(3)

async def check_market_status(subscribed_stocks):
    """每天早上9:15到9:16之间定期检查市场状态，并通知清洗服务"""
    while True:
        current_time = datetime.now().time()
        weekday = datetime.now().weekday()
        # 检查是否在周一到周五的9:15到9:17之间
        if weekday < 5 and time(9, 15) <= current_time <= time(9, 17):
            logger.info("正在检查市场状态...")
            for stock_code in subscribed_stocks:
                data = await fetch_stock_data(stock_code)
                if data:
                    send_to_processor(stock_code, data)

        await asyncio.sleep(20)  # 每20秒检查一次

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
