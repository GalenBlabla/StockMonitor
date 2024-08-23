from app.core.interfaces import Strategy
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PriceLimitAndOrderBookStrategy(Strategy):
    def __init__(self):
        self.last_notified_bid_volume = None
        self.last_notified_ask_volume = None

    def analyze(self, stock_code: str, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        buy_info = cleaned_data.get('buy_infos', [])
        ask_info = cleaned_data.get('ask_infos', [])
        origin_pankou = cleaned_data.get('origin_pankou', {})
        if not buy_info or not ask_info or not origin_pankou:
            logger.warning(f"{stock_code} 的数据缺失或为空，无法进行分析")
            return {"status": "no_data"}

        try:
            current_price = float(origin_pankou.get('currentPrice', 0))
            limit_up = float(origin_pankou.get('limitUp', 0))
            limit_down = float(origin_pankou.get('limitDown', 0))
            top_bid_volume = sum(int(info["bidvolume"]) for info in buy_info[:5])
            top_ask_volume = sum(int(info["askvolume"]) for info in ask_info[:5])

            if current_price == 0 or limit_up == 0 or limit_down == 0:
                logger.error(f"{stock_code} 的价格或涨跌停价为0，数据可能有误: current_price={current_price}, limit_up={limit_up}, limit_down={limit_down}")
                return {"status": "data_error", "price": current_price}

            logging.info(f"当前价格: {current_price}, 涨停价: {limit_up}, 跌停价: {limit_down}, 买单量: {top_bid_volume}, 卖单量: {top_ask_volume}")

            # 检查是否达到涨停或跌停
            status = None
            if current_price >= limit_up:
                status = "limit_up"
                logger.info(f"{stock_code} 已达到涨停价: {current_price}")
            elif current_price <= limit_down:
                status = "limit_down"
                logger.info(f"{stock_code} 已达到跌停价: {current_price}")

            # 检查买单封单量的变化百分比（涨停）
            if status == "limit_up" and self.last_notified_bid_volume is not None:
                bid_volume_change = abs(self.last_notified_bid_volume - top_bid_volume)
                bid_percentage_change = bid_volume_change / self.last_notified_bid_volume if self.last_notified_bid_volume != 0 else 0

                if bid_percentage_change >= 0.2:  # 判断买单封单量变化是否超过20%
                    bid_change_direction = "减少" if top_bid_volume < self.last_notified_bid_volume else "增加"
                    logger.warning(f"{stock_code} 涨停封单量急速{bid_change_direction}: 变化了 {bid_volume_change} 手 ({bid_percentage_change * 100:.2f}%)")
                    
                    self.last_notified_bid_volume = top_bid_volume

                    return {
                        "status": "bid_volume_change",
                        "current_price": current_price,
                        "bid_volume_change": bid_volume_change,
                        "top_bid_volume": top_bid_volume,
                        "bid_percentage_change": bid_percentage_change,
                        "message": f"涨停封单量急速{bid_change_direction}"
                    }

            # 检查卖单封单量的变化百分比（跌停）
            if status == "limit_down" and self.last_notified_ask_volume is not None:
                ask_volume_change = abs(self.last_notified_ask_volume - top_ask_volume)
                ask_percentage_change = ask_volume_change / self.last_notified_ask_volume if self.last_notified_ask_volume != 0 else 0

                if ask_percentage_change >= 0.2:  # 判断卖单封单量变化是否超过20%
                    ask_change_direction = "减少" if top_ask_volume < self.last_notified_ask_volume else "增加"
                    logger.warning(f"{stock_code} 跌停封单量急速{ask_change_direction}: 变化了 {ask_volume_change} 手 ({ask_percentage_change * 100:.2f}%)")
                    
                    self.last_notified_ask_volume = top_ask_volume

                    return {
                        "status": "ask_volume_change",
                        "current_price": current_price,
                        "ask_volume_change": ask_volume_change,
                        "top_ask_volume": top_ask_volume,
                        "ask_percentage_change": ask_percentage_change,
                        "message": f"跌停封单量急速{ask_change_direction}"
                    }

            # 更新最后通知的封单量
            self.last_notified_bid_volume = top_bid_volume
            self.last_notified_ask_volume = top_ask_volume

            return {
                "status": status or "normal",
                "current_price": current_price,
                "top_bid_volume": top_bid_volume,
                "top_ask_volume": top_ask_volume,
            }
        except (KeyError, ValueError) as e:
            logger.error(f"处理 {stock_code} 的数据时出错: {e}")
            return {"status": "error", "message": str(e)}
