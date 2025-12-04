# Shipping System Guide

This guide explains the internal shipping system for the e-commerce platform.

## Overview

The platform uses a simple internal shipping tracking system with support for multiple carriers:
- **Purolator** (Canadian primary)
- **FedEx** (International)
- **DHL** (International)
- **UPS** (North America)
- **Canada Post** (Canadian domestic)

**Important**: This is an internal tracking system. No external carrier APIs are integrated. All tracking numbers and shipment data are generated and managed within the application.

## How It Works

### 1. Carrier Selection

Carriers are selected via dropdown options in the UI. Available carriers are defined in `config.py`:

```python
DEFAULT_CARRIER: str = "purolator"
AVAILABLE_CARRIERS: List[str] = ["purolator", "fedex", "dhl", "ups", "canadapost"]
```

### 2. Tracking Number Generation

When a shipment is created, the system generates a carrier-specific tracking number format:

- **Purolator**: PU + 9 digits + CA (e.g., `PU123456789CA`)
- **FedEx**: 12 digits (e.g., `123456789012`)
- **DHL**: 10 digits (e.g., `1234567890`)
- **UPS**: 1Z + 6 alphanumeric + 8 digits (e.g., `1ZABC123456789012`)
- **Canada Post**: 13 digits (e.g., `1234567890123`)

### 3. Service Levels

Each carrier has predefined service levels:

**Purolator**:
- Express
- Ground

**FedEx**:
- Priority Overnight
- Express Saver
- Ground

**DHL**:
- Express Worldwide
- Economy Select

**UPS**:
- Next Day Air
- 2nd Day Air
- Ground

**Canada Post**:
- Priority
- Expedited Parcel
- Regular Parcel

### 4. Using the Shipping Service

```python
from Services.ShippingCarrierService import ShippingCarrierService

# Initialize service
shipping_service = ShippingCarrierService()

# Get available carriers
carriers = shipping_service.get_available_carriers()
# Returns: ["purolator", "fedex", "dhl", "ups", "canadapost"]

# Get service levels for a carrier
services = shipping_service.get_carrier_services("purolator")
# Returns: [
#     {"code": "express", "name": "Purolator Express"},
#     {"code": "ground", "name": "Purolator Ground"}
# ]

# Create a shipment
shipment = await shipping_service.create_shipment(
    carrier="purolator",
    service="express",
    origin={
        "address": "123 Warehouse St",
        "city": "Toronto",
        "state": "ON",
        "zip": "M5H 2N2",
        "country": "CA"
    },
    destination={
        "address": "456 Customer Ave",
        "city": "Vancouver",
        "state": "BC",
        "zip": "V6B 1A1",
        "country": "CA"
    },
    packages=[
        {
            "weight_grams": 1000,
            "length_cm": 30,
            "width_cm": 20,
            "height_cm": 10
        }
    ],
    order_id="ORD-12345"
)

# Result:
# {
#     "tracking_number": "PU123456789CA",
#     "carrier": "purolator",
#     "service": "express",
#     "status": "created",
#     "estimated_delivery": "2025-12-05T17:00:00Z",
#     "created_at": "2025-11-28T10:30:00Z"
# }

# Validate a carrier
is_valid = shipping_service.validate_carrier("fedex")
# Returns: True

# Generate a tracking number directly
tracking_number = shipping_service.generate_tracking_number("ups")
# Returns: "1ZABC123456789012"
```

### 5. Database Integration

Shipment data is stored in the `Delivery` model (Models/Delivery.py) with the following key fields:

- `carrier`: Selected carrier name (e.g., "purolator")
- `tracking_number`: Generated tracking number (e.g., "PU123456789CA")
- `service_level`: Selected service (e.g., "express", "ground")
- `status`: Current status (created, in_transit, delivered, etc.)
- `estimated_delivery_date`: Estimated delivery timestamp
- `actual_delivery_date`: Actual delivery timestamp (when delivered)
- `origin_address`: Sender address details
- `destination_address`: Recipient address details

### 6. Status Management

Shipment statuses are managed internally within your application:

- `created`: Shipment record created
- `picked_up`: Package picked up from origin
- `in_transit`: Package in transit to destination
- `out_for_delivery`: Package out for delivery
- `delivered`: Package delivered
- `exception`: Delivery exception occurred
- `cancelled`: Shipment cancelled

Update status through your Order management system or admin interface.

### 7. Frontend Integration

**Carrier Selection (Checkout)**:
```javascript
// Get available carriers
const response = await fetch('/api/shipping/carriers');
const carriers = await response.json();
// Returns: ["purolator", "fedex", "dhl", "ups", "canadapost"]

// Get service levels for selected carrier
const servicesResp = await fetch(`/api/shipping/carriers/${carrier}/services`);
const services = await servicesResp.json();
// Returns: [
//   {"code": "express", "name": "Purolator Express"},
//   {"code": "ground", "name": "Purolator Ground"}
// ]
```

**Create Shipment (Order Processing)**:
```javascript
const shipment = await fetch('/api/shipping/create', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    carrier: "purolator",
    service: "express",
    order_id: "ORD-12345",
    origin: {...},
    destination: {...},
    packages: [...]
  })
});

const result = await shipment.json();
// Returns: { tracking_number, carrier, service, status, estimated_delivery }
```

**Track Shipment (Customer Tracking Page)**:
```javascript
// Display tracking information
const tracking = await fetch(`/api/tracking/${trackingNumber}`);
const data = await tracking.json();

// Show:
// - Carrier name
// - Service level
// - Current status
// - Estimated delivery date
// - Tracking events history
```

## Configuration

All shipping configuration is in `config.py`:

```python
class Settings(BaseSettings):
    # Shipping Configuration (Internal Only - No External APIs)
    # All shipping is tracked internally within the company
    # Available carriers are predefined options, no API integration
    DEFAULT_CARRIER: str = "purolator"
    AVAILABLE_CARRIERS: List[str] = ["purolator", "fedex", "dhl", "ups", "canadapost"]
```

No API keys or external credentials are required. This keeps the system simple and focused on internal tracking.

## API Endpoints (To Implement)

These are suggested endpoints for your FastAPI application:

```python
# In your main API router

@router.get("/api/shipping/carriers")
async def get_carriers():
    """Get list of available carriers"""
    shipping_service = ShippingCarrierService()
    return shipping_service.get_available_carriers()

@router.get("/api/shipping/carriers/{carrier}/services")
async def get_carrier_services(carrier: str):
    """Get service levels for a specific carrier"""
    shipping_service = ShippingCarrierService()
    return shipping_service.get_carrier_services(carrier)

@router.post("/api/shipping/create")
async def create_shipment(request: CreateShipmentRequest):
    """Create a new shipment"""
    shipping_service = ShippingCarrierService()
    shipment = await shipping_service.create_shipment(
        carrier=request.carrier,
        service=request.service,
        origin=request.origin,
        destination=request.destination,
        packages=request.packages,
        order_id=request.order_id
    )
    
    # Save to database
    delivery_repo = DeliveryRepository()
    await delivery_repo.create(shipment)
    
    return shipment

@router.get("/api/tracking/{tracking_number}")
async def track_shipment(tracking_number: str):
    """Get tracking information"""
    delivery_repo = DeliveryRepository()
    delivery = await delivery_repo.get_by_tracking_number(tracking_number)
    
    if not delivery:
        raise HTTPException(status_code=404, detail="Tracking number not found")
    
    return {
        "tracking_number": delivery.tracking_number,
        "carrier": delivery.carrier,
        "service": delivery.service_level,
        "status": delivery.status,
        "estimated_delivery": delivery.estimated_delivery_date,
        "actual_delivery": delivery.actual_delivery_date,
        "events": delivery.tracking_events
    }
```

## Future Enhancements

If you decide to integrate real carrier APIs in the future:

1. **Rate Shopping**: Get real-time shipping quotes from multiple carriers
2. **Label Generation**: Generate actual shipping labels with barcodes
3. **Real-time Tracking**: Automatic status updates from carrier webhooks
4. **Address Validation**: Validate addresses before shipping
5. **Customs Documentation**: Generate commercial invoices for international shipments
6. **Insurance**: Add shipment insurance options
7. **Pickup Scheduling**: Schedule carrier pickups automatically

For now, the system provides a simple, internal-only tracking solution suitable for prototyping and development.

## Benefits of This Approach

1. **Simplicity**: No external API integration complexity
2. **No Costs**: No API usage fees or carrier account requirements
3. **Flexibility**: Easy to modify carrier options and tracking formats
4. **Prototyping**: Perfect for development and testing
5. **Privacy**: All data stays within your system
6. **Fast Development**: No waiting for API approvals or sandbox access

When you're ready to integrate real carrier APIs, you can gradually replace the internal tracking system with actual API calls while maintaining the same interface.
