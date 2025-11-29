"""
Purolator Carrier Adapter (MOCK/PROOF OF CONCEPT)

**SIMULATION MODE - No actual API calls are made**

This adapter simulates Purolator carrier behavior for:
- Tracking company deliveries (imports/exports)
- Demonstrating shipping workflows
- Testing without real carrier accounts

All tracking numbers, rates, and status updates are generated locally.
Perfect for development, demos, and proof of concept.
"""

import logging
import random
import string
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)


class PurolatorAdapter:
    """
    MOCK Purolator Adapter - Simulates carrier without external API calls.
    Tracks company imports/exports with realistic-looking data.
    """
    
    def __init__(self):
        self.carrier_name = "Purolator"
        self.services = {
            "express": {"name": "Purolator Express", "base_rate": 25.99, "days": 2},
            "ground": {"name": "Purolator Ground", "base_rate": 15.99, "days": 5},
            "overnight": {"name": "Purolator Overnight", "base_rate": 45.99, "days": 1}
        }
    
    async def get_rates(
        self,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        packages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        MOCK: Simulate Purolator shipping rate quotes.
        Generates realistic rates based on weight and distance.
        """
        logger.info(f"[MOCK] Simulating Purolator rates from {origin.get('zip')} to {destination.get('zip')}")
        
        # Calculate total weight
        total_weight_kg = sum(pkg.get("weight_grams", 1000) for pkg in packages) / 1000
        
        # Check if international
        is_international = origin.get("country", "CA") != destination.get("country", "CA")
        multiplier = 2.0 if is_international else 1.0
        
        # Generate mock rates for each service
        normalized_rates = []
        for service_code, service_info in self.services.items():
            base_cost = service_info["base_rate"]
            weight_surcharge = total_weight_kg * 5.0
            total_cost = (base_cost + weight_surcharge) * multiplier
            
            estimated_days = service_info["days"] * (1.5 if is_international else 1)
            delivery_date = datetime.now() + timedelta(days=estimated_days)
            
            normalized_rates.append({
                "carrier": "purolator",
                "service": service_code,
                "service_name": service_info["name"],
                "cost_cents": int(total_cost * 100),
                "currency": "CAD",
                "estimated_days": int(estimated_days),
                "estimated_delivery": delivery_date.isoformat(),
                "available": True
            })
        
        logger.info(f"[MOCK] Generated {len(normalized_rates)} simulated rates")
        return normalized_rates
    
    async def create_shipment(
        self,
        service: str,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        packages: List[Dict[str, Any]],
        reference: str,
        customs_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        MOCK: Simulate shipment creation for company deliveries.
        Generates fake tracking number and label URL.
        """
        logger.info(f"[MOCK] Simulating Purolator shipment for {reference}")
        
        # Generate mock tracking number
        tracking_number = f"PU{random.randint(100000000, 999999999)}CA"
        
        # Calculate delivery estimate
        service_info = self.services.get(service, self.services["ground"])
        is_international = origin.get("country", "CA") != destination.get("country", "CA")
        days = service_info["days"] * (1.5 if is_international else 1)
        delivery_date = datetime.now() + timedelta(days=days)
        
        # Calculate cost
        total_weight_kg = sum(pkg.get("weight_grams", 1000) for pkg in packages) / 1000
        cost = (service_info["base_rate"] + total_weight_kg * 5.0) * (2.0 if is_international else 1.0)
        
        # Generate mock URLs
        label_id = str(uuid4())
        
        logger.info(f"[MOCK] Generated tracking {tracking_number}")
        
        return {
            "tracking_number": tracking_number,
            "tracking_url": f"https://www.purolator.com/en/ship-track/tracking-summary?pin={tracking_number}",
            "label_url": f"https://cdn.yourstore.com/labels/purolator/{label_id}.pdf",
            "carrier": "purolator",
            "service": service,
            "estimated_delivery": delivery_date.isoformat(),
            "cost_cents": int(cost * 100),
            "customs_declaration_url": f"https://cdn.yourstore.com/customs/{label_id}.pdf" if customs_info else None
        }
    
    async def track(self, tracking_number: str) -> Dict[str, Any]:
        """
        MOCK: Simulate tracking status progression.
        Generates realistic tracking events for company deliveries.
        """
        logger.info(f"[MOCK] Simulating tracking for {tracking_number}")
        
        # Simulate status progression
        status_progression = [
            ("label_created", "Label created, awaiting pickup"),
            ("picked_up", "Package picked up by courier"),
            ("in_transit", "In transit to destination"),
            ("out_for_delivery", "Out for delivery"),
            ("delivered", "Successfully delivered")
        ]
        
        # Random current stage
        current_stage = random.randint(0, len(status_progression) - 1)
        current_status_code = status_progression[current_stage][0]
        
        # Generate tracking events
        events = []
        cities = ["Toronto, ON", "Montreal, QC", "Ottawa, ON", "Vancouver, BC"]
        base_time = datetime.now() - timedelta(days=2)
        
        for i in range(current_stage + 1):
            event_time = base_time + timedelta(hours=i * 8)
            status_code, description = status_progression[i]
            
            events.append({
                "timestamp": event_time.isoformat(),
                "status": status_code,
                "location": cities[min(i, len(cities) - 1)],
                "description": description
            })
        
        # Estimate delivery
        if current_status_code != "delivered":
            estimated_delivery = (datetime.now() + timedelta(days=random.randint(2, 5))).isoformat()
        else:
            estimated_delivery = events[-1]["timestamp"]
        
        logger.info(f"[MOCK] Package status: {current_status_code}")
        
        return {
            "tracking_number": tracking_number,
            "status": current_status_code,
            "current_location": events[-1]["location"] if events else None,
            "estimated_delivery": estimated_delivery,
            "events": events
        }
    
    async def cancel_shipment(self, tracking_number: str) -> bool:
        """MOCK: Simulate shipment cancellation."""
        logger.info(f"[MOCK] Simulating cancellation of {tracking_number}")
        # Always succeed in mock mode
        return True
    
    def normalize_status(self, purolator_status: str) -> str:
        """
        Translate Purolator status codes to unified status.
        
        Purolator statuses:
        - InfoReceived: Label created, not picked up yet
        - PickedUp: Carrier has package
        - InTransit: Moving between facilities
        - OutForDelivery: On delivery vehicle
        - Delivered: Successfully delivered
        - Exception: Problem occurred
        """
        status_map = {
            "InfoReceived": "label_created",
            "PickedUp": "picked_up",
            "InTransit": "in_transit",
            "OutForDelivery": "out_for_delivery",
            "Delivered": "delivered",
            "Exception": "exception",
            "AttemptFail": "delivery_failed",
            "CustomsHold": "customs_hold"
        }
        
        return status_map.get(purolator_status, "unknown")
    

