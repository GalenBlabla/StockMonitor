import httpx
import json
import logging
import asyncio
from datetime import datetime
import pika
from config import settings
from app.services.calendar_service import TradeCalendar

logger = logging.getLogger(__name__)

market_status = {}
calendar_service = TradeCalendar()

async def fetch_stock_data(stock_code: str):
    """从API获取股票数据"""
    if not await calendar_service.is_trading_day_and_time():
        logger.info(f"{stock_code}: 当前非交易时段或非交易日，跳过数据获取。")
        return None

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
            logger.info(response.url)
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
                data = await fetch_stock_data(stock_code)
                if data:
                    send_to_processor(stock_code, data)
        else:
            logger.info("没有订阅的股票，无需获取数据。")
        await asyncio.sleep(3)
