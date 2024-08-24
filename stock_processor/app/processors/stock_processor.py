# app/processors/stock_processor.py

from app.core.interfaces import DataCleaner, Strategy
from typing import Dict, Any, List
from app.core.events import AnalysisEvent

class StockProcessor:
    def __init__(self, cleaner: DataCleaner, strategies: Strategy):
        self.cleaner = cleaner
        self.strategies = strategies

    def process(self, stock_code: str, raw_data: Dict[str, Any]) -> List[AnalysisEvent]:
        cleaned_data = self.cleaner.clean(raw_data, stock_code)
        analysis_result = self.strategies.analyze(stock_code, cleaned_data)
        return analysis_result
