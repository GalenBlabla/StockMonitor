import json
import asyncio
import logging
from aio_pika import connect_robust, IncomingMessage
from config import settings

logging.getLogger('aio_pika').setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitorService:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def start(self):
        """启动异步监听"""
        self.connection = await connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()

        # 声明队列
        await self.channel.declare_queue('user_management_status', durable=False)
        await self.channel.declare_queue('stock_fetcher_status', durable=False)
        await self.channel.declare_queue('stock_processor_status', durable=False)

        # 注册不同的回调函数来处理各个服务的数据
        await self.channel.set_qos(prefetch_count=1)
        
        user_management_queue = await self.channel.get_queue('user_management_status')
        stock_fetcher_queue = await self.channel.get_queue('stock_fetcher_status')
        stock_processor_queue = await self.channel.get_queue('stock_processor_status')

        await user_management_queue.consume(self.user_management_callback)
        await stock_fetcher_queue.consume(self.stock_fetcher_callback)
        await stock_processor_queue.consume(self.stock_processor_callback)
        logger.info("MonitorService 已连接到 RabbitMQ，开始监听各服务状态...")
        await asyncio.Future()  # 阻止函数退出，保持监听状态

    async def user_management_callback(self, message: IncomingMessage):
        """处理 User Management 服务的上报数据"""
        async with message.process():
            data = json.loads(message.body.decode())
            logger.info(f"接收到 User Management 服务的数据: {data}")
            # 在这里处理数据并存储或进一步操作

    async def stock_fetcher_callback(self, message: IncomingMessage):
        """处理 Stock Fetcher 服务的上报数据"""
        async with message.process():
            data = json.loads(message.body.decode())
            logger.info(f"接收到 Stock Fetcher 服务的数据: {data}")
            # 在这里处理数据并存储或进一步操作

    async def stock_processor_callback(self, message: IncomingMessage):
        """处理 Stock Processor 服务的上报数据"""
        async with message.process():
            data = json.loads(message.body.decode())
            logger.info(f"接收到 Stock Processor 服务的数据: {data}")
            # 在这里处理数据并存储或进一步操作

    async def stop(self):
        """关闭连接"""
        if self.connection:
            await self.connection.close()

if __name__ == "__main__":
    monitor_service = MonitorService()
    try:
        asyncio.run(monitor_service.start())
    except KeyboardInterrupt:
        logger.info("MonitorService 停止中...")
        asyncio.run(monitor_service.stop())
        logger.info("MonitorService 已停止。")
