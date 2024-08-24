# app/processors/strategy_combiner.py

from typing import List, Dict, Any
from app.core.interfaces import Strategy
from app.core.events import AnalysisEvent

class StrategyCombiner:
    def __init__(self, strategies: List[Strategy]):
        self.strategies = strategies

    def analyze(self, stock_code: str, cleaned_data: Dict[str, Any]) -> List[AnalysisEvent]:
        events = []
        for strategy in self.strategies:
            event = strategy.analyze(stock_code, cleaned_data)
            events.append(event)
        return events
