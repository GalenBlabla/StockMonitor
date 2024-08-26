from abc import ABC, abstractmethod
from typing import Dict, Any

class DataCleaner(ABC):
    @abstractmethod
    def clean(self, raw_data: Dict[str, Any], stock_code: str) -> Dict[str, Any]:
        pass

class Strategy(ABC):
    @abstractmethod
    async def analyze(self, stock_code: str, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class Notifier(ABC):
    @abstractmethod
    async def notify(self, stock_code: str, analysis_result: Dict[str, Any]):
        pass
