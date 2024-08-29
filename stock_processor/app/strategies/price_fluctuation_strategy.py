from core.interfaces import Strategy
from typing import Dict, Any
import logging
from core.events import AnalysisEvent

logger = logging.getLogger(__name__)

class PriceFluctuationStrategy(Strategy):
    async def analyze(self, stock_code: str, cleaned_data: Dict[str, Any]) -> AnalysisEvent:
        if cleaned_data.get('market_status') == "交易中":
            fluctuation = self.detect_price_fluctuation(cleaned_data)
            if fluctuation and abs(fluctuation) > 1.0:
                return AnalysisEvent("price_fluctuation", stock_code, {"fluctuation": fluctuation})
        return AnalysisEvent("normal", stock_code, {"fluctuation": 0})

    def detect_price_fluctuation(self, cleaned_data: Dict[str, Any]) -> float:
        price_info = cleaned_data.get('price_info', [])
        if len(price_info) >= 2:
            price_now = float(price_info[-1]["price"])
            price_old = float(price_info[-2]["price"])
            return round(((price_now - price_old) / price_old) * 100, 2)
        return 0.0
