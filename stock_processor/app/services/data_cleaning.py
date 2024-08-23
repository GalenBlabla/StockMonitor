from app.core.interfaces import DataCleaner
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class DefaultDataCleaner(DataCleaner):
    def clean(self, raw_data: Dict[str, Any], stock_code: str) -> Dict[str, Any]:
        try:
            result = raw_data.get('Result', {})
            cleaned_data = {
                'result_code': raw_data.get('ResultCode'),
                'update_info': result.get('update'),
                'provider_info': result.get('provider'),
                'origin_pankou': result.get('pankouinfos', {}).get('origin_pankou'),
                'pankou_info': result.get('pankouinfos', {}).get('list'),
                'new_market_data': result.get('newMarketData'),
                'member_info': result.get('member_info'),
                'detail_info': result.get('detailinfos'),
                'cur_info': result.get('cur'),
                'buy_infos': result.get('buyinfos'),
                'basic_infos': result.get('basicinfos'),
                'ask_infos': result.get('askinfos'),
                'price_info': result.get('priceinfo'),
                'market_status': result.get('update', {}).get('stockStatus'),
            }
            return cleaned_data
        except Exception as e:
            logger.error(f"Error cleaning stock data: {e}")
            return {}
