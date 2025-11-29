"""
Canada Post Carrier Adapter (Template)

Canada Post REST API: https://www.canadapost.ca/cpo/mc/business/productsservices/developers.jsf
Authentication: API Key + Secret (HTTP Basic Auth)
Features: Domestic and international shipping within/from Canada
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CanadaPostAdapter:
    """Adapter for Canada Post API (REST/XML based)."""
    
    def __init__(self):
        from config import settings
        self.api_key = settings.CANADAPOST_API_KEY
        self.api_secret = settings.CANADAPOST_API_SECRET
        self.customer_number = settings.CANADAPOST_CUSTOMER_NUMBER
        self.base_url = settings.CANADAPOST_BASE_URL
    
    async def get_rates(self, origin, destination, packages) -> List[Dict]:
        logger.warning("Canada Post adapter not yet implemented")
        return []
    
    async def create_shipment(self, service, origin, destination, packages, reference, customs_info=None) -> Dict:
        raise NotImplementedError("Canada Post adapter not yet implemented")
    
    async def track(self, tracking_number: str) -> Dict:
        raise NotImplementedError("Canada Post adapter not yet implemented")
    
    async def cancel_shipment(self, tracking_number: str) -> bool:
        return False
    
    def normalize_status(self, canadapost_status: str) -> str:
        status_map = {
            "In Transit": "in_transit",
            "Delivered": "delivered",
            "Failed": "delivery_failed"
        }
        return status_map.get(canadapost_status, "unknown")
