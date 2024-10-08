from core.interfaces import Strategy
from core.events import AnalysisEvent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class RapidMovementStrategy(Strategy):
    async def analyze(self, stock_code: str, cleaned_data: Dict[str, Any]) -> AnalysisEvent:
        price_info = cleaned_data.get('price_info', [])
        if len(price_info) >= 5:
            recent_prices = [float(info["price"]) for info in price_info[-5:]]
            fluctuation = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
            if abs(fluctuation) > 2.0:  # 根据需求调整这个阈值
                return AnalysisEvent(
                    event_type="rapid_movement_5m",
                    stock_code=stock_code,
                    data={"fluctuation": fluctuation}
                )
        return AnalysisEvent(
            event_type="normal",
            stock_code=stock_code,
            data={"fluctuation": 0}
        )
