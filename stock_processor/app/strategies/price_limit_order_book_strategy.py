from core.interfaces import Strategy
from core.events import AnalysisEvent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PriceLimitAndOrderBookStrategy(Strategy):
    def __init__(self):
        self.initial_bid_volume = None  # 初始的买单封单量
        self.initial_ask_volume = None  # 初始的卖单封单量

    async def analyze(self, stock_code: str,  cleaned_data: Dict[str, Any]) -> AnalysisEvent:
        buy_info = cleaned_data.get('buy_infos', [])
        ask_info = cleaned_data.get('ask_infos', [])
        origin_pankou = cleaned_data.get('origin_pankou', {})

        if not buy_info or not ask_info or not origin_pankou:
            logger.warning(f"{ stock_code} 的数据缺失或为空，无法进行分析{cleaned_data}")
            return AnalysisEvent(event_type="no_data", stock_code=stock_code, data={"status": "no_data"})

        try:
            current_price = float(origin_pankou.get('currentPrice', 0))
            limit_up = float(origin_pankou.get('limitUp', 0))
            limit_down = float(origin_pankou.get('limitDown', 0))
            top_bid_volume = sum(int(info["bidvolume"]) for info in buy_info[:5])
            top_ask_volume = sum(int(info["askvolume"]) for info in ask_info[:5])

            if current_price == 0 or limit_up == 0 or limit_down == 0:
                logger.error(f"{stock_code} 的价格或涨跌停价为0，数据可能有误: current_price={current_price}, limit_up={limit_up}, limit_down={limit_down}")
                return AnalysisEvent(event_type="data_error", stock_code=stock_code,  data={"status": "data_error", "price": current_price})

            logging.info(f"当前价格: {current_price}, 涨停价: {limit_up}, 跌停价: {limit_down}, 买单量: {top_bid_volume}, 卖单量: {top_ask_volume}")

            # 初始化封单量（首次处理该股票）
            if self.initial_bid_volume is None:
                self.initial_bid_volume = top_bid_volume
                self.initial_ask_volume = top_ask_volume
                # logger.info(f"{stock_code} 初始化封单量: 买单量: {self.initial_bid_volume}, 卖单量: {self.initial_ask_volume}")
                return AnalysisEvent(
                    event_type="normal",
                    stock_code=stock_code,
                    data={
                        "current_price": current_price,
                        "top_bid_volume": top_bid_volume,
                        "top_ask_volume": top_ask_volume,
                    }
                )

            # 检查封单量变化（涨停状态下的买单，跌停状态下的卖单）
            status = None
            if current_price >= limit_up:  # 涨停
                bid_volume_change = abs(self.initial_bid_volume - top_bid_volume)
                if bid_volume_change != 0:
                    logger.info(f"{stock_code} 涨停封单量变化: 初始量 {self.initial_bid_volume}, 当前量 {top_bid_volume}, 变化 {bid_volume_change}")
                    self.initial_bid_volume = top_bid_volume  # 更新封单量
                    status = "bid_volume_change"
                    return AnalysisEvent(
                        event_type=status,
                        stock_code=stock_code,
                        data={
                            "current_price": current_price,
                            "bid_volume_change": bid_volume_change,
                            "top_bid_volume": top_bid_volume,
                            "message": "涨停封单量变化"
                        }
                    )
            elif current_price <= limit_down:  # 跌停
                ask_volume_change = abs(self.initial_ask_volume - top_ask_volume)
                if ask_volume_change != 0:
                    # logger.info(f"{stock_code} 跌停封单量变化: 初始量 {self.initial_ask_volume}, 当前量 {top_ask_volume}, 变化 {ask_volume_change}")
                    self.initial_ask_volume = top_ask_volume  # 更新封单量
                    status = "ask_volume_change"
                    return AnalysisEvent(
                        event_type=status,
                        stock_code=stock_code,
                        data={
                            "current_price": current_price,
                            "ask_volume_change": ask_volume_change,
                            "top_ask_volume": top_ask_volume,
                            "message": "跌停封单量变化"
                        }
                    )

            return AnalysisEvent(
                event_type="normal",
                stock_code=stock_code,
                data={
                    "current_price": current_price,
                    "top_bid_volume": top_bid_volume,
                    "top_ask_volume": top_ask_volume,
                }
            )
        except (KeyError, ValueError) as e:
            logger.error(f"处理 {stock_code} 的数据时出错: {e}")
            return AnalysisEvent(event_type="error", stock_code=stock_code, data={"status": "error", "message": str(e)})
