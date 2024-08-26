# app/processors/stock_processor.py

from core.interfaces import DataCleaner, Strategy
from typing import Dict, Any, List
from core.events import AnalysisEvent

class StockProcessor:
    def __init__(self, cleaner: DataCleaner, strategy_combiner: Strategy):
        self.cleaner = cleaner
        self.strategy_combiner = strategy_combiner

    async def process(self, stock_code: str, raw_data: Dict[str, Any]) -> List[AnalysisEvent]:
        cleaned_data = self.cleaner.clean(raw_data, stock_code)
        # 调用 strategy_combiner 的 analyze 方法，该方法内部并行执行所有策略
        analysis_results = await self.strategy_combiner.analyze(stock_code, cleaned_data)
        return analysis_results
