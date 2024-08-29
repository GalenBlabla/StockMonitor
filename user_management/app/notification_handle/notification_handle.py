from app.core.event_bus import event_handler
from app.core.events import NotificationEvent
from app.api.v1.services.rabbitmq_service import send_processed_event  # 导入新的发送函数
import logging

logger = logging.getLogger(__name__)

# 用于跟踪每个股票代码的当前状态
stock_state = {}

@event_handler("limit_up")
async def handle_limit_up(event: NotificationEvent):
    stock_code = event.stock_code
    current_state = stock_state.get(stock_code, "normal")
    
    # 如果状态没有变化，则不通知
    if current_state == "limit_up":
        logger.info(f"股票 {stock_code} 已经处于涨停状态，不重复通知。")
        return

    logger.info(f"处理涨停事件: {stock_code} 数据: {event.data}")
    stock_state[stock_code] = "limit_up"  # 更新状态
    await send_processed_event(event)  # 上报处理后的结果

@event_handler("limit_down")
async def handle_limit_down(event: NotificationEvent):
    stock_code = event.stock_code
    current_state = stock_state.get(stock_code, "normal")
    
    # 如果状态没有变化，则不通知
    if current_state == "limit_down":
        logger.info(f"股票 {stock_code} 已经处于跌停状态，不重复通知。")
        return
    logger.info(f"处理跌停事件: {stock_code} 数据: {event.data}")
    stock_state[stock_code] = "limit_down"  # 更新状态
    await send_processed_event(event)  # 上报处理后的结果

@event_handler("price_fluctuation")
async def handle_price_fluctuation(event: NotificationEvent):
    logger.info(f"价格波动事件: {event.stock_code} 数据: {event.data}")
    # 实现价格波动事件的处理逻辑
    await send_processed_event(event)  # 上报处理后的结果

@event_handler("rapid_movement_5m")
async def handle_rapid_movement(event: NotificationEvent):
    logger.info(f"处理快速波动事件: {event.stock_code} 数据: {event.data}")
    # 实现快速波动事件的处理逻辑
    await send_processed_event(event)  # 上报处理后的结果

@event_handler("ask_volume_change")
async def handle_ask_volume_change(event: NotificationEvent):
    logger.info(f"处理卖单量变化事件: {event.stock_code} 数据: {event.data}")
    # 实现卖单量变化事件的处理逻辑
    await send_processed_event(event)  # 上报处理后的结果

@event_handler("bid_volume_change")
async def handle_bid_volume_change(event: NotificationEvent):
    logger.info(f"处理买单量变化事件: {event.stock_code} 数据: {event.data}")
    # 实现买单量变化事件的处理逻辑
    await send_processed_event(event)  # 上报处理后的结果

@event_handler("normal")
async def handle_normal(event: NotificationEvent):
    pass

@event_handler("error")
async def handle_error(event: NotificationEvent):
    pass
