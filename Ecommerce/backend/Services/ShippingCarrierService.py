"""
Simple Shipping Carrier Service

This is a mock/internal-only shipping system for prototype purposes.
No external carrier APIs are used - all carriers, tracking numbers, and
statuses are managed internally within the application.

Available Carriers (dropdown options):
    - Purolator
    - FedEx
    - DHL
    - UPS
    - Canada Post

All tracking numbers and shipping data are generated internally.
"""

import logging
import random
import string
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config import settings

logger = logging.getLogger(__name__)


class ShippingCarrierService:
    """
    Internal shipping tracking service.
    
    Provides simple carrier selection and tracking number generation.
    No external API calls are made - this is for internal tracking only.
    """
    
    def __init__(self):
        """Initialize with available carrier options from config."""
        self.available_carriers = settings.AVAILABLE_CARRIERS
        self.default_carrier = settings.DEFAULT_CARRIER
        logger.info(f"Shipping service initialized with carriers: {', '.join(self.available_carriers)}")
    
    def get_available_carriers(self) -> List[str]:
        """
        Get list of available carriers for dropdown selection.
        
        Returns:
            ["purolator", "fedex", "dhl", "ups", "canadapost"]
        """
        return self.available_carriers.copy()
    
    def generate_tracking_number(self, carrier: str) -> str:
        """
        Generate a mock tracking number for the specified carrier.
        
        Args:
            carrier: One of the available carriers
        
        Returns:
            Generated tracking number string (e.g., "PU123456789CA")
        """
        if carrier not in self.available_carriers:
            raise ValueError(f"Invalid carrier: {carrier}. Must be one of {self.available_carriers}")
        
        # Generate carrier-specific tracking number formats
        if carrier == "purolator":
            # Purolator format: PU + 9 digits + CA
            return f"PU{''.join(random.choices(string.digits, k=9))}CA"
        elif carrier == "fedex":
            # FedEx format: 12-14 digits
            return ''.join(random.choices(string.digits, k=12))
        elif carrier == "dhl":
            # DHL format: 10 digits
            return ''.join(random.choices(string.digits, k=10))
        elif carrier == "ups":
            # UPS format: 1Z + 6 alphanumeric + 8 digits
            return f"1Z{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}{''.join(random.choices(string.digits, k=8))}"
        elif carrier == "canadapost":
            # Canada Post format: 13 digits
            return ''.join(random.choices(string.digits, k=13))
        else:
            # Generic format
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    async def create_shipment(
        self,
        carrier: str,
        service: str,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        packages: List[Dict[str, Any]],
        order_id: str
    ) -> Dict[str, Any]:
        """
        Create internal shipment record with generated tracking number.
        
        Args:
            carrier: One of the available carriers (e.g., "purolator")
            service: Service level (e.g., "express", "ground", "priority")
            origin: Sender address dict
            destination: Recipient address dict
            packages: List of package dimensions
            order_id: Reference order ID
        
        Returns:
            {
                "tracking_number": "PU123456789CA",
                "carrier": "purolator",
                "service": "express",
                "status": "created",
                "estimated_delivery": "2025-12-05T17:00:00Z"
            }
        """
        logger.info(f"Creating internal shipment record for order {order_id} with {carrier}")
        
        if carrier not in self.available_carriers:
            raise ValueError(f"Invalid carrier: {carrier}")
        
        tracking_number = self.generate_tracking_number(carrier)
        estimated_delivery = datetime.utcnow() + timedelta(days=random.randint(2, 5))
        
        shipment_data = {
            "tracking_number": tracking_number,
            "carrier": carrier,
            "service": service,
            "status": "created",
            "estimated_delivery": estimated_delivery.isoformat() + "Z",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        logger.info(f"Generated tracking number {tracking_number} for order {order_id}")
        return shipment_data
    
    def get_carrier_services(self, carrier: str) -> List[Dict[str, str]]:
        """
        Get available service levels for a carrier.
        
        Args:
            carrier: Carrier name
        
        Returns:
            List of service options with labels
        """
        services = {
            "purolator": [
                {"code": "express", "name": "Purolator Express"},
                {"code": "ground", "name": "Purolator Ground"}
            ],
            "fedex": [
                {"code": "priority", "name": "FedEx Priority Overnight"},
                {"code": "express", "name": "FedEx Express Saver"},
                {"code": "ground", "name": "FedEx Ground"}
            ],
            "dhl": [
                {"code": "express", "name": "DHL Express Worldwide"},
                {"code": "economy", "name": "DHL Economy Select"}
            ],
            "ups": [
                {"code": "next_day", "name": "UPS Next Day Air"},
                {"code": "2day", "name": "UPS 2nd Day Air"},
                {"code": "ground", "name": "UPS Ground"}
            ],
            "canadapost": [
                {"code": "priority", "name": "Priority"},
                {"code": "expedited", "name": "Expedited Parcel"},
                {"code": "regular", "name": "Regular Parcel"}
            ]
        }
        
        return services.get(carrier, [{"code": "standard", "name": "Standard Shipping"}])
    
    def validate_carrier(self, carrier: str) -> bool:
        """Check if carrier is in available carriers list."""
        return carrier in self.available_carriers
