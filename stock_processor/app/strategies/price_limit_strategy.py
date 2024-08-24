from app.core.interfaces import Strategy
from typing import Dict, Any
import logging
from app.core.events import AnalysisEvent

logger = logging.getLogger(__name__)

class PriceLimitStrategy(Strategy):
    def analyze(self, stock_code: str, cleaned_data: Dict[str, Any]) -> AnalysisEvent:
        origin_pankou = cleaned_data.get('origin_pankou', {})
        
        if not origin_pankou:
            logger.warning(f"{stock_code} 的盘口数据为空，无法进行涨跌停分析")
            return AnalysisEvent("no_data", stock_code, {"status": "no_data"})

        try:
            current_price = float(origin_pankou.get('currentPrice', 0))
            limit_up = float(origin_pankou.get('limitUp', 0))
            limit_down = float(origin_pankou.get('limitDown', 0))

            if current_price == 0 or limit_up == 0 or limit_down == 0:
                logger.error(f"{stock_code} 的价格或涨跌停价为0，数据可能有误: current_price={current_price}, limit_up={limit_up}, limit_down={limit_down}")
                return AnalysisEvent("data_error", stock_code, {
                    "status": "data_error",
                    "price": current_price
                })

            logging.info(f"当前价格: {current_price}, 涨停价: {limit_up}, 跌停价: {limit_down}")

            # 检查是否达到涨停或跌停
            if current_price >= limit_up:
                logger.info(f"{stock_code} 已达到涨停价: {current_price}")
                return AnalysisEvent("limit_up", stock_code, {
                    "status": "limit_up",
                    "current_price": current_price,
                    "limit_up": limit_up,
                    "message": f"{stock_code} 已达到涨停价: {current_price}"
                })
            elif current_price <= limit_down:
                logger.info(f"{stock_code} 已达到跌停价: {current_price}")
                return AnalysisEvent("limit_down", stock_code, {
                    "status": "limit_down",
                    "current_price": current_price,
                    "limit_down": limit_down,
                    "message": f"{stock_code} 已达到跌停价: {current_price}"
                })

            # 如果没有达到涨停或跌停
            return AnalysisEvent("normal", stock_code, {
                "status": "normal",
                "current_price": current_price,
                "message": f"{stock_code} 当前价格正常: {current_price}"
            })

        except (KeyError, ValueError) as e:
            logger.error(f"处理 {stock_code} 的数据时出错: {e}")
            return AnalysisEvent("error", stock_code, {
                "status": "error",
                "message": str(e)
            })
