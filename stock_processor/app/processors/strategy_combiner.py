# app/processors/strategy_combiner.py

from typing import List, Dict, Any
from app.core.interfaces import Strategy

class StrategyCombiner:
    def __init__(self, strategies: List[Strategy]):
        self.strategies = strategies

    def analyze(self, stock_code: str, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        combined_results = {}
        for strategy in self.strategies:
            result = strategy.analyze(stock_code, cleaned_data)
            combined_results.update(result)
        return combined_results
