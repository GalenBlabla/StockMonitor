# app/processors/stock_processor.py

from app.core.interfaces import DataCleaner, Notifier, Strategy
from typing import Dict, Any

class StockProcessor:
    def __init__(self, cleaner: DataCleaner, strategies: Strategy, notifier: Notifier):
        self.cleaner = cleaner
        self.strategies = strategies
        self.notifier = notifier

    def process(self, stock_code: str, raw_data: Dict[str, Any]):
        cleaned_data = self.cleaner.clean(raw_data, stock_code)
        analysis_result = self.strategies.analyze(stock_code, cleaned_data)
        self.notifier.notify(stock_code, analysis_result)
