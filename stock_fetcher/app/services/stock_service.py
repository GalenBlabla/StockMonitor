import httpx
import json
import logging
import asyncio
from config import settings
from services.calendar_service import TradeCalendar
from aio_pika import connect_robust, Message

logger = logging.getLogger(__name__)

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
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"获取股票 {stock_code} 数据时出错: {e}")
        return None

async def send_to_processor(stock_code: str, data: dict):
    """将股票数据发送到 Stock Processor 服务"""
    try:
        connection = await connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()
        await channel.declare_queue('stock_data', durable=False)

        message = {
            'stock_code': stock_code,
            'data': data
        }

        await channel.default_exchange.publish(
            Message(body=json.dumps(message).encode()),
            routing_key='stock_data'
        )
        logger.info(f"已将 {stock_code} 的数据发送到 Stock Processor 服务")
    except Exception as e:
        logger.error(f"发送数据到处理服务失败: {e}")
    finally:
        await connection.close()

async def periodic_stock_fetch(subscribed_stocks):
    """每3秒获取一次所有订阅股票的最新数据"""
    while True:
        if subscribed_stocks:
            for stock_code in subscribed_stocks:
                data = await fetch_stock_data(stock_code)
                if data:
                    await send_to_processor(stock_code, data)
        else:
            logger.info("没有订阅的股票，无需获取数据。")
        await asyncio.sleep(3)
