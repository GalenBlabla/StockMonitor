import asyncio
import logging
from config import settings
from services.stock_service import periodic_stock_fetch
from services.rabbitmq_service import start_rabbitmq_listener,report_status

# 设置 pika 的日志级别为 WARNING 或更高，以隐藏调试和信息日志
logging.getLogger('aio_pika').setLevel(logging.WARNING)
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

subscribed_stocks = set()

async def main():
    # 并行启动RabbitMQ监听器、股票数据定时获取任务和状态上报任务
    while True:
        try:
            await asyncio.gather(
                start_rabbitmq_listener(subscribed_stocks),
                periodic_stock_fetch(subscribed_stocks),
                report_status()
            )
        except Exception as e:
            logger.error(f"主循环中发生错误: {e}")
            await asyncio.sleep(50)  # 如果出现异常，等待5秒再继续运行

if __name__ == "__main__":
    asyncio.run(main())
