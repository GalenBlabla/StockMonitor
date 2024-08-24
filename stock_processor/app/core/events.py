from typing import Dict, Any

class AnalysisEvent:
    def __init__(self, event_type: str, stock_code: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.stock_code = stock_code
        self.data = data

    def to_dict(self):
        return {
            "event_type": self.event_type,
            "stock_code": self.stock_code,
            "data": self.data
        }
