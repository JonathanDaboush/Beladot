"""
Comprehensive tests for ShippingCarrierService.

Tests cover:
- Carrier list retrieval
- Tracking number generation
- Service level validation
- Carrier validation
- Shipment creation
- Edge cases and error handling
"""
import pytest
from Services.ShippingCarrierService import ShippingCarrierService
from config import settings


class TestShippingCarrierService:
    """Test suite for ShippingCarrierService."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = ShippingCarrierService()
        assert service.available_carriers is not None
        assert service.default_carrier is not None
        assert isinstance(service.available_carriers, list)
        assert len(service.available_carriers) > 0
    
    def test_get_available_carriers(self):
        """Test retrieving available carriers."""
        service = ShippingCarrierService()
        carriers = service.get_available_carriers()
        
        assert isinstance(carriers, list)
        assert len(carriers) == 5
        assert "purolator" in carriers
        assert "fedex" in carriers
        assert "dhl" in carriers
        assert "ups" in carriers
        assert "canadapost" in carriers
    
    def test_get_available_carriers_returns_copy(self):
        """Test that get_available_carriers returns a copy."""
        service = ShippingCarrierService()
        carriers1 = service.get_available_carriers()
        carriers2 = service.get_available_carriers()
        
        # Modify one list
        carriers1.append("fake_carrier")
        
        # Original should be unchanged
        carriers2 = service.get_available_carriers()
        assert "fake_carrier" not in carriers2
    
    def test_validate_carrier_valid(self):
        """Test validating valid carriers."""
        service = ShippingCarrierService()
        
        assert service.validate_carrier("purolator") is True
        assert service.validate_carrier("fedex") is True
        assert service.validate_carrier("dhl") is True
        assert service.validate_carrier("ups") is True
        assert service.validate_carrier("canadapost") is True
    
    def test_validate_carrier_invalid(self):
        """Test validating invalid carriers."""
        service = ShippingCarrierService()
        
        assert service.validate_carrier("invalid_carrier") is False
        assert service.validate_carrier("") is False
        assert service.validate_carrier("FEDEX") is False  # Case sensitive
        assert service.validate_carrier("usps") is False  # Not in list
    
    def test_generate_tracking_number_purolator(self):
        """Test Purolator tracking number generation."""
        service = ShippingCarrierService()
        tracking = service.generate_tracking_number("purolator")
        
        assert tracking.startswith("PU")
        assert tracking.endswith("CA")
        assert len(tracking) == 13  # PU + 9 digits + CA
        assert tracking[2:11].isdigit()
    
    def test_generate_tracking_number_fedex(self):
        """Test FedEx tracking number generation."""
        service = ShippingCarrierService()
        tracking = service.generate_tracking_number("fedex")
        
        assert len(tracking) == 12
        assert tracking.isdigit()
    
    def test_generate_tracking_number_dhl(self):
        """Test DHL tracking number generation."""
        service = ShippingCarrierService()
        tracking = service.generate_tracking_number("dhl")
        
        assert len(tracking) == 10
        assert tracking.isdigit()
    
    def test_generate_tracking_number_ups(self):
        """Test UPS tracking number generation."""
        service = ShippingCarrierService()
        tracking = service.generate_tracking_number("ups")
        
        assert tracking.startswith("1Z")
        assert len(tracking) == 16  # 1Z + 6 alphanumeric + 8 digits
        assert tracking[8:].isdigit()  # Last 8 are digits
    
    def test_generate_tracking_number_canadapost(self):
        """Test Canada Post tracking number generation."""
        service = ShippingCarrierService()
        tracking = service.generate_tracking_number("canadapost")
        
        assert len(tracking) == 13
        assert tracking.isdigit()
    
    def test_generate_tracking_number_invalid_carrier(self):
        """Test tracking number generation with invalid carrier."""
        service = ShippingCarrierService()
        
        with pytest.raises(ValueError) as exc_info:
            service.generate_tracking_number("invalid_carrier")
        
        assert "Invalid carrier" in str(exc_info.value)
    
    def test_generate_tracking_number_uniqueness(self):
        """Test that tracking numbers are unique."""
        service = ShippingCarrierService()
        tracking_numbers = set()
        
        # Generate 100 tracking numbers
        for _ in range(100):
            tracking = service.generate_tracking_number("purolator")
            tracking_numbers.add(tracking)
        
        # All should be unique
        assert len(tracking_numbers) == 100
    
    def test_get_carrier_services_purolator(self):
        """Test getting Purolator service levels."""
        service = ShippingCarrierService()
        services = service.get_carrier_services("purolator")
        
        assert isinstance(services, list)
        assert len(services) == 2
        assert any(s["code"] == "express" for s in services)
        assert any(s["code"] == "ground" for s in services)
    
    def test_get_carrier_services_fedex(self):
        """Test getting FedEx service levels."""
        service = ShippingCarrierService()
        services = service.get_carrier_services("fedex")
        
        assert isinstance(services, list)
        assert len(services) == 3
        assert any(s["code"] == "priority" for s in services)
        assert any(s["code"] == "express" for s in services)
        assert any(s["code"] == "ground" for s in services)
    
    def test_get_carrier_services_dhl(self):
        """Test getting DHL service levels."""
        service = ShippingCarrierService()
        services = service.get_carrier_services("dhl")
        
        assert isinstance(services, list)
        assert len(services) == 2
        assert any(s["code"] == "express" for s in services)
        assert any(s["code"] == "economy" for s in services)
    
    def test_get_carrier_services_ups(self):
        """Test getting UPS service levels."""
        service = ShippingCarrierService()
        services = service.get_carrier_services("ups")
        
        assert isinstance(services, list)
        assert len(services) == 3
        assert any(s["code"] == "next_day" for s in services)
        assert any(s["code"] == "2day" for s in services)
        assert any(s["code"] == "ground" for s in services)
    
    def test_get_carrier_services_canadapost(self):
        """Test getting Canada Post service levels."""
        service = ShippingCarrierService()
        services = service.get_carrier_services("canadapost")
        
        assert isinstance(services, list)
        assert len(services) == 3
        assert any(s["code"] == "priority" for s in services)
        assert any(s["code"] == "expedited" for s in services)
        assert any(s["code"] == "regular" for s in services)
    
    def test_get_carrier_services_invalid_carrier(self):
        """Test getting services for invalid carrier returns default."""
        service = ShippingCarrierService()
        services = service.get_carrier_services("invalid_carrier")
        
        assert isinstance(services, list)
        assert len(services) == 1
        assert services[0]["code"] == "standard"
    
    @pytest.mark.asyncio
    async def test_create_shipment_success(self):
        """Test successful shipment creation."""
        service = ShippingCarrierService()
        
        shipment = await service.create_shipment(
            carrier="purolator",
            service="express",
            origin={
                "address": "123 Main St",
                "city": "Toronto",
                "state": "ON",
                "zip": "M5H 2N2",
                "country": "CA"
            },
            destination={
                "address": "456 Oak Ave",
                "city": "Vancouver",
                "state": "BC",
                "zip": "V6B 1A1",
                "country": "CA"
            },
            packages=[{"weight_grams": 1000, "length_cm": 30, "width_cm": 20, "height_cm": 10}],
            order_id="ORD-12345"
        )
        
        assert shipment is not None
        assert "tracking_number" in shipment
        assert shipment["carrier"] == "purolator"
        assert shipment["service"] == "express"
        assert shipment["status"] == "created"
        assert "estimated_delivery" in shipment
        assert "created_at" in shipment
    
    @pytest.mark.asyncio
    async def test_create_shipment_invalid_carrier(self):
        """Test shipment creation with invalid carrier."""
        service = ShippingCarrierService()
        
        with pytest.raises(ValueError) as exc_info:
            await service.create_shipment(
                carrier="invalid_carrier",
                service="express",
                origin={},
                destination={},
                packages=[],
                order_id="ORD-12345"
            )
        
        assert "Invalid carrier" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_shipment_all_carriers(self):
        """Test shipment creation with all carriers."""
        service = ShippingCarrierService()
        carriers = service.get_available_carriers()
        
        for carrier in carriers:
            shipment = await service.create_shipment(
                carrier=carrier,
                service="express",
                origin={},
                destination={},
                packages=[],
                order_id=f"ORD-{carrier}"
            )
            
            assert shipment["carrier"] == carrier
            assert shipment["tracking_number"] is not None
    
    @pytest.mark.asyncio
    async def test_create_shipment_estimated_delivery(self):
        """Test that shipment has valid estimated delivery."""
        service = ShippingCarrierService()
        
        shipment = await service.create_shipment(
            carrier="fedex",
            service="priority",
            origin={},
            destination={},
            packages=[],
            order_id="ORD-99999"
        )
        
        from datetime import datetime
        estimated = datetime.fromisoformat(shipment["estimated_delivery"].replace("Z", "+00:00"))
        created = datetime.fromisoformat(shipment["created_at"].replace("Z", "+00:00"))
        
        # Estimated delivery should be after creation
        assert estimated > created
        
        # Should be within reasonable range (2-5 days)
        delta = (estimated - created).days
        assert 2 <= delta <= 5
    
    def test_default_carrier_is_valid(self):
        """Test that default carrier is in available carriers."""
        service = ShippingCarrierService()
        
        assert service.default_carrier in service.available_carriers
    
    def test_carrier_services_have_required_fields(self):
        """Test that all carrier services have required fields."""
        service = ShippingCarrierService()
        carriers = service.get_available_carriers()
        
        for carrier in carriers:
            services = service.get_carrier_services(carrier)
            
            for svc in services:
                assert "code" in svc
                assert "name" in svc
                assert isinstance(svc["code"], str)
                assert isinstance(svc["name"], str)
                assert len(svc["code"]) > 0
                assert len(svc["name"]) > 0
