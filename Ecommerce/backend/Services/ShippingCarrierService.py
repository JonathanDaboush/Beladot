"""
Multi-Carrier Shipping Orchestrator Service

Your platform integrates with third-party carriers (Purolator, FedEx, DHL, UPS, Canada Post)
to provide shipping rates, generate labels, and track packages. You don't own the delivery
infrastructure - you orchestrate it.

Architecture:
    - Adapter Pattern: Each carrier has its own adapter translating API calls
    - Rate Shopping: Get quotes from multiple carriers, show best options
    - Webhook Handler: Carriers push status updates to your endpoints
    - Polling Fallback: Background job for carriers without webhooks
    
Integration Flow:
    1. Checkout: get_rates() → show shipping options
    2. Order Paid: create_shipment() → generate label, get tracking number
    3. Real-time Updates: Webhooks → update delivery status, send emails
    4. Backup Polling: Background job → sync tracking for missing webhooks
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import settings
from Ecommerce.backend.Services.Carriers.PurolatorAdapter import PurolatorAdapter
from Ecommerce.backend.Services.Carriers.FedExAdapter import FedExAdapter
from Ecommerce.backend.Services.Carriers.DHLAdapter import DHLAdapter
from Ecommerce.backend.Services.Carriers.UPSAdapter import UPSAdapter
from Ecommerce.backend.Services.Carriers.CanadaPostAdapter import CanadaPostAdapter

logger = logging.getLogger(__name__)


class ShippingCarrierService:
    """
    Multi-carrier shipping orchestration service.
    
    Abstracts carrier-specific APIs behind a unified interface. Your system
    doesn't do shipping - it coordinates with external carriers.
    """
    
    def __init__(self):
        """Initialize carrier adapters based on configuration."""
        self.carriers = {}
        
        # Initialize enabled carriers (check if API keys configured)
        if settings.PUROLATOR_API_KEY:
            self.carriers["purolator"] = PurolatorAdapter()
            logger.info("Purolator adapter initialized")
        
        if settings.FEDEX_API_KEY:
            self.carriers["fedex"] = FedExAdapter()
            logger.info("FedEx adapter initialized")
        
        if settings.DHL_API_KEY:
            self.carriers["dhl"] = DHLAdapter()
            logger.info("DHL adapter initialized")
        
        if settings.UPS_CLIENT_ID:
            self.carriers["ups"] = UPSAdapter()
            logger.info("UPS adapter initialized")
        
        if settings.CANADAPOST_API_KEY:
            self.carriers["canadapost"] = CanadaPostAdapter()
            logger.info("Canada Post adapter initialized")
        
        if not self.carriers:
            logger.warning("No carrier adapters configured. Add API keys to config.")
    
    async def get_rates(
        self,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        packages: List[Dict[str, Any]],
        carriers: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get shipping quotes from multiple carriers (rate shopping).
        
        Called at checkout to display shipping options to customer.
        
        Args:
            origin: {"address": "123 Main St", "city": "Toronto", "state": "ON", "zip": "M5H 2N2", "country": "CA"}
            destination: Same format as origin
            packages: [{"weight_grams": 1000, "length_cm": 30, "width_cm": 20, "height_cm": 10, "value_cents": 5000}]
            carriers: Optional list of carriers to query (default: all enabled)
        
        Returns:
            [
                {
                    "carrier": "purolator",
                    "service": "express",
                    "service_name": "Purolator Express",
                    "cost_cents": 2599,
                    "currency": "CAD",
                    "estimated_days": 2,
                    "estimated_delivery": "2025-11-30T17:00:00Z",
                    "available": true
                },
                {
                    "carrier": "fedex",
                    "service": "priority",
                    "service_name": "FedEx Priority Overnight",
                    "cost_cents": 2850,
                    "currency": "CAD",
                    "estimated_days": 1,
                    "estimated_delivery": "2025-11-29T10:30:00Z",
                    "available": true
                }
            ]
        
        Business Logic:
            - Queries all enabled carriers in parallel
            - Filters unavailable services (e.g., dangerous goods restrictions)
            - Sorts by cost or speed (configurable)
            - Caches results for 5 minutes (rates don't change frequently)
        """
        logger.info(f"Getting shipping rates from {origin['city']} to {destination['city']}")
        
        # Determine which carriers to query
        target_carriers = carriers or list(self.carriers.keys())
        
        if not target_carriers:
            logger.error("No carriers available for rate shopping")
            return []
        
        # Query carriers in parallel (asyncio.gather)
        rates = []
        for carrier_name in target_carriers:
            if carrier_name not in self.carriers:
                logger.warning(f"Carrier {carrier_name} not configured, skipping")
                continue
            
            try:
                adapter = self.carriers[carrier_name]
                carrier_rates = await adapter.get_rates(origin, destination, packages)
                rates.extend(carrier_rates)
                logger.info(f"Got {len(carrier_rates)} rates from {carrier_name}")
            except Exception as e:
                logger.error(f"Failed to get rates from {carrier_name}: {e}", exc_info=True)
                # Continue with other carriers (don't fail entire checkout)
        
        # Sort by cost (cheapest first) or speed (fastest first)
        if settings.ENABLE_CARRIER_RATE_SHOPPING:
            rates.sort(key=lambda x: x["cost_cents"])  # Cheapest first
        
        logger.info(f"Returning {len(rates)} total shipping options")
        return rates
    
    async def create_shipment(
        self,
        carrier: str,
        service: str,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        packages: List[Dict[str, Any]],
        order_id: str,
        customs_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate shipping label from carrier API.
        
        Called after order is paid and ready to ship. Creates shipment with carrier,
        gets tracking number and label PDF.
        
        Args:
            carrier: "purolator", "fedex", "dhl", "ups", "canadapost"
            service: Service level code from get_rates() (e.g., "express", "ground")
            origin: Warehouse/sender address
            destination: Customer address
            packages: Package dimensions and weight
            order_id: Your internal order ID (for reference)
            customs_info: For international shipments: {"value_cents": 10000, "currency": "USD", "items": [...]}
        
        Returns:
            {
                "tracking_number": "PU123456789CA",
                "tracking_url": "https://www.purolator.com/track?pin=PU123456789CA",
                "label_url": "https://cdn.purolator.com/labels/xyz.pdf",
                "carrier": "purolator",
                "service": "express",
                "estimated_delivery": "2025-11-30T17:00:00Z",
                "cost_cents": 2599,
                "customs_declaration_url": "https://cdn.purolator.com/customs/xyz.pdf"  # If international
            }
        
        Side Effects:
            - Creates shipment in carrier's system (can't be undone easily)
            - Charges your carrier account (usually on pickup or delivery)
            - Generates label PDF (must be printed and attached to package)
        """
        logger.info(f"Creating {carrier} shipment for order {order_id}")
        
        if carrier not in self.carriers:
            logger.error(f"Carrier {carrier} not configured")
            raise ValueError(f"Carrier {carrier} not available")
        
        try:
            adapter = self.carriers[carrier]
            shipment_data = await adapter.create_shipment(
                service=service,
                origin=origin,
                destination=destination,
                packages=packages,
                reference=order_id,
                customs_info=customs_info
            )
            
            logger.info(f"Created shipment {shipment_data['tracking_number']} for order {order_id}")
            return shipment_data
            
        except Exception as e:
            logger.error(f"Failed to create shipment with {carrier}: {e}", exc_info=True)
            raise
    
    async def track_shipment(self, carrier: str, tracking_number: str) -> Dict[str, Any]:
        """
        Get current tracking status from carrier API.
        
        Called by background job (polling) or on-demand (customer tracking page).
        
        Args:
            carrier: "purolator", "fedex", etc.
            tracking_number: Carrier's tracking ID
        
        Returns:
            {
                "tracking_number": "PU123456789CA",
                "status": "in_transit",  # Normalized status
                "current_location": "Montreal, QC",
                "estimated_delivery": "2025-11-30T17:00:00Z",
                "events": [
                    {
                        "timestamp": "2025-11-28T10:30:00Z",
                        "status": "picked_up",
                        "location": "Toronto, ON",
                        "description": "Package picked up from sender"
                    },
                    {
                        "timestamp": "2025-11-28T14:15:00Z",
                        "status": "in_transit",
                        "location": "Montreal, QC",
                        "description": "Arrived at sort facility"
                    }
                ]
            }
        """
        logger.info(f"Tracking {carrier} shipment {tracking_number}")
        
        if carrier not in self.carriers:
            logger.error(f"Carrier {carrier} not configured")
            raise ValueError(f"Carrier {carrier} not available")
        
        try:
            adapter = self.carriers[carrier]
            tracking_data = await adapter.track(tracking_number)
            
            logger.info(f"Tracking status for {tracking_number}: {tracking_data['status']}")
            return tracking_data
            
        except Exception as e:
            logger.error(f"Failed to track shipment {tracking_number}: {e}", exc_info=True)
            raise
    
    async def create_return_label(
        self,
        carrier: str,
        service: str,
        origin: Dict[str, Any],  # Customer's address (sender for return)
        destination: Dict[str, Any],  # Your warehouse (receiver for return)
        packages: List[Dict[str, Any]],
        order_id: str
    ) -> Dict[str, Any]:
        """
        Generate return shipping label for customer.
        
        Customer initiated a return, provide them a label to send item back.
        
        Args:
            carrier: Same carrier as original shipment (or different)
            service: Usually cheaper service for returns (ground)
            origin: Customer address (they're sending it back)
            destination: Your warehouse/return center
            packages: Return package dimensions
            order_id: Original order ID for reference
        
        Returns:
            Same format as create_shipment() - tracking number and label PDF
        
        Business Logic:
            - You pay for return shipping (customer satisfaction)
            - Or customer pays (subtract from refund amount)
            - Label emailed to customer, they print and attach
        """
        logger.info(f"Creating return label for order {order_id}")
        
        # Return labels are just shipments in reverse direction
        return await self.create_shipment(
            carrier=carrier,
            service=service,
            origin=origin,
            destination=destination,
            packages=packages,
            order_id=f"RET-{order_id}",
            customs_info=None  # Returns usually don't need customs (domestic)
        )
    
    async def cancel_shipment(self, carrier: str, tracking_number: str) -> bool:
        """
        Cancel shipment before pickup (void label).
        
        Only works if carrier hasn't picked up package yet. Prevents being charged.
        
        Returns:
            True if cancelled successfully, False if already picked up
        """
        logger.info(f"Attempting to cancel {carrier} shipment {tracking_number}")
        
        if carrier not in self.carriers:
            logger.error(f"Carrier {carrier} not configured")
            return False
        
        try:
            adapter = self.carriers[carrier]
            cancelled = await adapter.cancel_shipment(tracking_number)
            
            if cancelled:
                logger.info(f"Successfully cancelled shipment {tracking_number}")
            else:
                logger.warning(f"Could not cancel {tracking_number} (may already be picked up)")
            
            return cancelled
            
        except Exception as e:
            logger.error(f"Failed to cancel shipment {tracking_number}: {e}", exc_info=True)
            return False
    
    def normalize_status(self, carrier: str, carrier_status: str) -> str:
        """
        Translate carrier-specific status codes to unified status.
        
        Each carrier has different status codes:
        - Purolator: "InfoReceived", "InTransit", "Delivered"
        - FedEx: "OC", "IT", "DL"
        - DHL: "transit", "delivered"
        
        We normalize to: created, picked_up, in_transit, out_for_delivery, delivered, exception
        """
        if carrier in self.carriers:
            return self.carriers[carrier].normalize_status(carrier_status)
        return "unknown"
