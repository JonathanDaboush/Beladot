# Carrier Integration Implementation Guide

This guide will help you implement production-ready carrier API integrations for your e-commerce platform.

## Overview

Your platform integrates with 5 major carriers:
- **Purolator** (Canadian primary)
- **FedEx** (International)
- **DHL** (International)
- **UPS** (North America)
- **Canada Post** (Canadian domestic)

## Phase 1: Account Setup (Week 1)

### 1.1 Purolator Developer Account
1. Visit: https://developer.purolator.com/
2. Register for developer account
3. Request sandbox credentials
4. Get production credentials (requires business verification)
5. Obtain:
   - API Key
   - API Secret
   - Account Number
   - Webhook Secret

**Documentation**: https://developer.purolator.com/docs

### 1.2 FedEx Developer Account
1. Visit: https://developer.fedex.com/
2. Create FedEx Developer account
3. Register your application
4. Request test credentials
5. Apply for production access (requires FedEx account)
6. Obtain:
   - API Key (Client ID)
   - Secret Key (Client Secret)
   - Account Number
   - Meter Number

**Documentation**: https://developer.fedex.com/api/en-us/catalog.html

### 1.3 DHL Developer Account
1. Visit: https://developer.dhl.com/
2. Sign up for API access
3. Subscribe to:
   - DHL Express Rating API
   - DHL Express Shipment API
   - DHL Express Tracking API
4. Get sandbox keys
5. Request production access
6. Obtain:
   - API Key
   - API Secret
   - Account Number

**Documentation**: https://developer.dhl.com/api-reference

### 1.4 UPS Developer Account
1. Visit: https://developer.ups.com/
2. Register for UPS My Choice for Business
3. Create application in UPS Developer Portal
4. Request OAuth 2.0 credentials
5. Obtain:
   - Client ID
   - Client Secret
   - Account Number

**Documentation**: https://developer.ups.com/api/reference

### 1.5 Canada Post Developer Account
1. Visit: https://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/
2. Register for Canada Post Developer Program
3. Request API credentials
4. Obtain:
   - API Key
   - API Secret
   - Customer Number

**Documentation**: https://www.canadapost.ca/information/app/drc/home

## Phase 2: Environment Configuration (Week 1)

### 2.1 Create .env File

Create `.env` in the backend directory:

```env
# Purolator
PUROLATOR_API_KEY=your_purolator_api_key
PUROLATOR_API_SECRET=your_purolator_api_secret
PUROLATOR_ACCOUNT_NUMBER=your_purolator_account
PUROLATOR_BASE_URL=https://webservices.purolator.com/PWS/V2
PUROLATOR_WEBHOOK_SECRET=your_webhook_secret_32chars

# FedEx
FEDEX_API_KEY=your_fedex_client_id
FEDEX_SECRET_KEY=your_fedex_client_secret
FEDEX_ACCOUNT_NUMBER=your_fedex_account
FEDEX_METER_NUMBER=your_meter_number
FEDEX_BASE_URL=https://apis.fedex.com
FEDEX_WEBHOOK_SECRET=your_webhook_secret_32chars

# DHL
DHL_API_KEY=your_dhl_api_key
DHL_API_SECRET=your_dhl_api_secret
DHL_ACCOUNT_NUMBER=your_dhl_account
DHL_BASE_URL=https://api.dhl.com
DHL_WEBHOOK_SECRET=your_webhook_secret_32chars

# UPS
UPS_CLIENT_ID=your_ups_client_id
UPS_CLIENT_SECRET=your_ups_client_secret
UPS_ACCOUNT_NUMBER=your_ups_account
UPS_BASE_URL=https://onlinetools.ups.com/api
UPS_WEBHOOK_SECRET=your_webhook_secret_32chars

# Canada Post
CANADAPOST_API_KEY=your_canadapost_key
CANADAPOST_API_SECRET=your_canadapost_secret
CANADAPOST_CUSTOMER_NUMBER=your_customer_number
CANADAPOST_BASE_URL=https://ct.soa-gw.canadapost.ca

# Shipping Config
DEFAULT_CARRIER=purolator
ENABLE_CARRIER_RATE_SHOPPING=true
TRACKING_SYNC_INTERVAL_MINUTES=15
```

### 2.2 Install Dependencies

Add to `requirements.txt`:
```
httpx>=0.24.0  # Async HTTP client
zeep>=4.2.0  # SOAP client for Purolator
python-jose>=3.3.0  # JWT for webhooks
```

Install:
```bash
pip install -r requirements.txt
```

## Phase 3: Complete Carrier Adapters (Week 2-3)

### 3.1 Purolator Adapter
**Status**: Template complete, needs SOAP implementation  
**File**: `Services/Carriers/PurolatorAdapter.py`

**Required Changes**:
1. Install zeep library: `pip install zeep`
2. Replace JSON requests with SOAP/XML:
```python
from zeep import Client
from zeep.wsse.username import UsernameToken

# In __init__
self.soap_client = Client(
    f"{self.base_url}/EstimatingService.asmx?wsdl",
    wsse=UsernameToken(self.api_key, self.api_secret)
)
```

3. Update `get_rates()` to use SOAP:
```python
response = self.soap_client.service.GetFullEstimate(
    BillingAccountNumber=self.account_number,
    SenderPostalCode=origin["zip"],
    ReceiverAddress={...},
    # ... full SOAP structure
)
```

**Testing**: Use Purolator sandbox first  
**Timeline**: 2-3 days

### 3.2 FedEx Adapter
**Status**: Placeholder, needs full implementation  
**File**: `Services/Carriers/FedExAdapter.py`

**Implementation Steps**:
1. OAuth 2.0 authentication:
```python
async def _get_access_token(self):
    response = await httpx.post(
        f"{self.base_url}/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
    )
    return response.json()["access_token"]
```

2. Rate API call:
```python
async def get_rates(self, origin, destination, packages):
    token = await self._get_access_token()
    response = await httpx.post(
        f"{self.base_url}/rate/v1/rates/quotes",
        headers={"Authorization": f"Bearer {token}"},
        json={...}  # FedEx rate request structure
    )
```

**API Reference**: https://developer.fedex.com/api/en-us/catalog/rate/v1/docs.html  
**Timeline**: 3-4 days

### 3.3 DHL Adapter
**Status**: Placeholder  
**File**: `Services/Carriers/DHLAdapter.py`

**Key Points**:
- REST/JSON API (easiest to implement)
- Basic auth with API key
- Strong international customs support
- Real-time tracking

**API Reference**: https://developer.dhl.com/api-reference/express-rating  
**Timeline**: 2-3 days

### 3.4 UPS Adapter
**Status**: Placeholder  
**File**: `Services/Carriers/UPSAdapter.py`

**Key Points**:
- OAuth 2.0 (similar to FedEx)
- REST/JSON API
- Complex shipment creation
- Excellent returns handling

**API Reference**: https://developer.ups.com/api/reference?loc=en_US  
**Timeline**: 3-4 days

### 3.5 Canada Post Adapter
**Status**: Placeholder  
**File**: `Services/Carriers/CanadaPostAdapter.py`

**Key Points**:
- REST/XML API (hybrid)
- Basic auth
- Domestic Canada only
- Simple integration

**API Reference**: https://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/rating.page  
**Timeline**: 2 days

## Phase 4: Webhook Implementation (Week 3)

### 4.1 Create Webhook Endpoints

Create `Services/WebhookHandler.py`:

```python
from fastapi import APIRouter, Request, HTTPException, Header
import hmac
import hashlib
from config import settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature"""
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@router.post("/purolator/tracking")
async def purolator_webhook(
    request: Request,
    x_purolator_signature: str = Header(None)
):
    """Handle Purolator tracking updates"""
    body = await request.body()
    
    if not verify_signature(body, x_purolator_signature, settings.PUROLATOR_WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = await request.json()
    
    # Update delivery in database
    from Repositories.DeliveryRepository import DeliveryRepository
    from Services.EmailService import send_tracking_update
    
    delivery = await DeliveryRepository.get_by_tracking_number(data["tracking_number"])
    if delivery:
        await DeliveryRepository.update_tracking_info(
            delivery.id,
            data["events"]
        )
        
        # Send email notifications
        if data["status"] == "delivered":
            await send_delivered(delivery.user.email, ...)
    
    return {"status": "ok"}

# Repeat for other carriers
@router.post("/fedex/tracking")
async def fedex_webhook(request: Request): ...

@router.post("/dhl/tracking")
async def dhl_webhook(request: Request): ...

@router.post("/ups/tracking")
async def ups_webhook(request: Request): ...
```

### 4.2 Register Webhooks with Carriers

Each carrier requires webhook registration:

**Purolator**:
```bash
curl -X POST https://webservices.purolator.com/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "url": "https://yourstore.com/webhooks/purolator/tracking",
    "events": ["tracking.updated", "delivery.completed"]
  }'
```

**Repeat for FedEx, DHL, UPS** (each has different registration process)

## Phase 5: Background Tracking Sync (Week 3)

### 5.1 Create Polling Job

Create `Jobs/sync_tracking.py`:

```python
import asyncio
from datetime import datetime, timedelta
from Repositories.DeliveryRepository import DeliveryRepository
from Services.ShippingCarrierService import ShippingCarrierService

async def sync_in_transit_deliveries():
    """
    Poll carriers for tracking updates.
    Fallback for carriers without webhooks or webhook failures.
    """
    delivery_repo = DeliveryRepository()
    carrier_service = ShippingCarrierService()
    
    # Get all in-transit deliveries
    deliveries = await delivery_repo.get_in_transit_deliveries()
    
    for delivery in deliveries:
        try:
            # Query carrier for latest status
            tracking_data = await carrier_service.track_shipment(
                delivery.carrier,
                delivery.tracking_number
            )
            
            # Update database
            await delivery_repo.update_tracking_info(
                delivery.id,
                tracking_data["events"]
            )
            
            # Send notifications if status changed significantly
            if tracking_data["status"] == "delivered":
                from Utilities.email import send_delivered
                await send_delivered(
                    delivery.user.email,
                    delivery.tracking_number,
                    # ... other params
                )
            
        except Exception as e:
            logger.error(f"Failed to sync tracking for {delivery.id}: {e}")
            continue

if __name__ == "__main__":
    asyncio.run(sync_in_transit_deliveries())
```

### 5.2 Schedule with Cron

Add to crontab (Linux/Mac) or Task Scheduler (Windows):

```cron
*/15 * * * * cd /path/to/backend && python Jobs/sync_tracking.py
```

Or use APScheduler in your FastAPI app:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(
    sync_in_transit_deliveries,
    'interval',
    minutes=settings.TRACKING_SYNC_INTERVAL_MINUTES
)
scheduler.start()
```

## Phase 6: Frontend Integration (Week 4)

### 6.1 Checkout Flow

```javascript
// Get shipping rates
const rates = await fetch('/api/shipping/rates', {
  method: 'POST',
  body: JSON.stringify({
    origin: warehouseAddress,
    destination: customerAddress,
    packages: [{
      weight_grams: totalWeight,
      length_cm: 30,
      width_cm: 20,
      height_cm: 15
    }]
  })
});

// Display rates to customer
rates.forEach(rate => {
  // Show: carrier, service, cost, estimated delivery
});

// Create shipment when order placed
const shipment = await fetch('/api/shipping/create', {
  method: 'POST',
  body: JSON.stringify({
    carrier: selectedCarrier,
    service: selectedService,
    order_id: orderId
  })
});
```

### 6.2 Tracking Page

```javascript
// Customer tracking page
const tracking = await fetch(`/api/tracking/${trackingNumber}`);

// Display:
// - Current status
// - Estimated delivery
// - Tracking events timeline
// - Map (if available)
```

### 6.3 Admin Dashboard

```javascript
// Admin label printing
const label = await fetch(`/api/admin/shipments/${shipmentId}/label`);
window.open(label.label_url, '_blank');

// Bulk label printing
const labels = await fetch('/api/admin/shipments/batch-labels', {
  method: 'POST',
  body: JSON.stringify({ shipment_ids: [...] })
});
```

## Phase 7: Testing (Ongoing)

### 7.1 Sandbox Testing

Test each carrier in sandbox mode:

1. **Rate Shopping**: Query all carriers, compare responses
2. **Label Generation**: Create test shipments
3. **Tracking**: Simulate package movement
4. **Webhooks**: Use carrier test events
5. **Cancellations**: Void shipments

### 7.2 Production Testing

1. Start with low-volume carrier (Canada Post)
2. Create real shipments with tracking
3. Monitor webhook delivery
4. Verify email notifications
5. Test customer tracking page
6. Gradually enable other carriers

### 7.3 Error Handling

Test failure scenarios:
- API timeout (10s+)
- Invalid credentials
- Rate limit exceeded
- Carrier downtime
- Invalid address
- Package too heavy

## Phase 8: Monitoring & Optimization

### 8.1 Logging

Add structured logging:

```python
import structlog

logger = structlog.get_logger()

logger.info("shipment_created", 
    carrier="purolator",
    tracking_number="PU123456789CA",
    order_id=12345,
    cost_cents=2599
)
```

### 8.2 Metrics

Track:
- Rate shopping response times
- Shipment creation success rate
- Tracking sync frequency
- Webhook delivery rate
- Carrier API errors

### 8.3 Cost Optimization

- Enable rate shopping to find cheapest carrier
- Negotiate carrier discounts based on volume
- Use ground shipping when possible
- Consolidate multiple items into single shipment
- Compare dimensional vs actual weight pricing

## Security Checklist

- [ ] API credentials stored in environment variables (not code)
- [ ] Webhook signature verification implemented
- [ ] HTTPS only for all carrier communication
- [ ] Rate limiting on webhook endpoints
- [ ] API key rotation schedule defined
- [ ] Audit logging for all shipment operations
- [ ] Customer data (addresses) encrypted at rest
- [ ] PCI compliance for payment + shipping integration

## Go-Live Checklist

- [ ] All carrier accounts approved for production
- [ ] Environment variables configured
- [ ] Webhook endpoints registered with all carriers
- [ ] Background tracking job scheduled
- [ ] Email templates tested
- [ ] Frontend checkout flow complete
- [ ] Customer tracking page live
- [ ] Admin dashboard functional
- [ ] Error monitoring setup (Sentry, etc.)
- [ ] Load testing completed
- [ ] Backup plan if primary carrier fails

## Support & Resources

### Carrier Support
- **Purolator**: developer-support@purolator.com
- **FedEx**: https://developer.fedex.com/support
- **DHL**: dhl.developer@dhl.com
- **UPS**: developersupport@ups.com
- **Canada Post**: devportal-supportportaidev@canadapost.ca

### Recommended Libraries
- `httpx` - Async HTTP client
- `zeep` - SOAP/WSDL client (Purolator)
- `python-jose` - JWT/webhooks
- `apscheduler` - Background jobs
- `structlog` - Structured logging

## Estimated Timeline

- **Week 1**: Account setup, credentials, environment config
- **Week 2**: Implement Purolator + FedEx adapters
- **Week 3**: Implement DHL/UPS/Canada Post, webhooks, background jobs
- **Week 4**: Frontend integration, testing
- **Week 5**: Production testing, optimization
- **Week 6**: Go-live

**Total**: 6 weeks for full production-ready implementation

## Next Steps

1. **Immediate**: Register for Purolator and FedEx developer accounts (longest approval time)
2. **Day 2-3**: Set up .env file with sandbox credentials
3. **Day 4-7**: Complete Purolator adapter implementation and test in sandbox
4. **Week 2**: Add FedEx adapter, test both carriers together
5. **Week 3**: Complete remaining carriers + webhooks
6. **Week 4**: Frontend integration
7. **Week 5-6**: Production testing and optimization
