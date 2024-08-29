import json
from core.interfaces import Strategy
from core.events import AnalysisEvent
from typing import Dict, Any
import logging
from services.redis_service import redis_client  # 导入 Redis 客户端

logger = logging.getLogger(__name__)

class PriceLimitAndOrderBookStrategy(Strategy):
    def __init__(self):
        self.change_threshold = 0.2  # 封单量变化的比例阈值
        self.expiration_time = 6 * 3600

    def _get_initial_volumes(self, stock_code: str):
        """从 Redis 中获取初始买单和卖单封单量"""
        data = redis_client.get(stock_code)
        if data:
            volumes = json.loads(data)
            return volumes.get('bid_volume'), volumes.get('ask_volume')
        return None, None

    def _set_initial_volumes(self, stock_code: str, bid_volume: float, ask_volume: float):
        """将初始买单和卖单封单量存储到 Redis 中"""
        volumes = {
            'bid_volume': bid_volume,
            'ask_volume': ask_volume
        }
        redis_client.set(stock_code, self.expiration_time, json.dumps(volumes))

    async def analyze(self, stock_code: str, cleaned_data: Dict[str, Any]) -> AnalysisEvent:
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
            top_bid_volume = int(buy_info[0]["bidvolume"])/100 if buy_info else 0  # 只显示买一的量
            top_ask_volume = int(ask_info[0]["askvolume"])/100 if ask_info else 0  # 只显示卖一的量

            if current_price == 0 or limit_up == 0 or limit_down == 0:
                return AnalysisEvent(event_type="data_error", stock_code=stock_code,  data={"status": "data_error", "price": current_price})

            # 从 Redis 中获取初始封单量
            initial_bid_volume, initial_ask_volume = self._get_initial_volumes(stock_code)

            # 初始化封单量（首次处理该股票）
            if initial_bid_volume is None or initial_ask_volume is None:
                self._set_initial_volumes(stock_code, top_bid_volume, top_ask_volume)
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
                bid_volume_change = abs(initial_bid_volume - top_bid_volume)
                if initial_bid_volume > 0:
                    bid_volume_change_ratio = bid_volume_change / initial_bid_volume
                    logger.info(f"bid_volume_change_ratio:{bid_volume_change_ratio},bid_volume_change{bid_volume_change},initial_bid_volume{initial_bid_volume}")
                    if bid_volume_change_ratio >= self.change_threshold:
                        self._set_initial_volumes(stock_code, top_bid_volume, initial_ask_volume)  # 更新封单量到 Redis
                        status = "bid_volume_change"
                        return AnalysisEvent(
                            event_type=status,
                            stock_code=stock_code,
                            data={
                                "current_price": current_price,
                                "bid_volume_change": bid_volume_change,
                                "bid_volume_change_ratio": bid_volume_change_ratio,
                                "top_bid_volume": top_bid_volume,
                                "message": f"涨停封单量变化超过{self.change_threshold*100}%"
                            }
                        )
            elif current_price <= limit_down:  # 跌停
                ask_volume_change = abs(initial_ask_volume - top_ask_volume)
                if initial_ask_volume > 0:
                    ask_volume_change_ratio = ask_volume_change / initial_ask_volume
                    logger.info(f"ask_volume_change_ratio:{ask_volume_change_ratio},ask_volume_change:{ask_volume_change},initial_ask_volume:{initial_ask_volume}")
                    if ask_volume_change_ratio >= self.change_threshold:
                        self._set_initial_volumes(stock_code, initial_bid_volume, top_ask_volume)  # 更新封单量到 Redis
                        status = "ask_volume_change"
                        return AnalysisEvent(
                            event_type=status,
                            stock_code=stock_code,
                            data={
                                "current_price": current_price,
                                "ask_volume_change": ask_volume_change,
                                "ask_volume_change_ratio": ask_volume_change_ratio,
                                "top_ask_volume": top_ask_volume,
                                "message": f"跌停封单量变化超过{self.change_threshold*100}%"
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
