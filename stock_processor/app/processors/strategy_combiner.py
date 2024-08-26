# app/processors/strategy_combiner.py

from typing import List, Dict, Any
from core.interfaces import Strategy
from core.events import AnalysisEvent
import asyncio

class StrategyCombiner:
    def __init__(self, strategies: List[Strategy]):
        self.strategies = strategies

    async def analyze(self, stock_code: str, cleaned_data: Dict[str, Any]) -> List[AnalysisEvent]:
        # 并行执行所有策略的 analyze 方法
        analysis_results = await asyncio.gather(
            *(strategy.analyze(stock_code, cleaned_data) for strategy in self.strategies)
        )
        # 过滤掉返回None的结果
        return [result for result in analysis_results if result is not None]
