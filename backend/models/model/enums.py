"""
enums.py

Defines enums for statuses and resolutions used throughout the backend models and services.
Includes shipment, refund, user account, reimbursement, incident, product, and shipping statuses.
"""

from enum import Enum

# Shipment Issue
class ShipmentIssueResolution(Enum):
    UNRESOLVED = 'unresolved'
    SELLER_FAULT = 'seller_fault'
    SHIPMENT_FAULT = 'shipment_fault'

# Refund Request
class RefundRequestStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    DENIED = 'denied'

# User Account
class UserAccountStatus(Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    DELETED = 'deleted'

# Reimbursement
class ReimbursementStatus(Enum):
    PENDING = 'pending'
    AWAITING_FINANCE_REVIEW = 'awaiting_finance_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PAID = 'paid'

# Incident
class IncidentStatus(Enum):
    OPEN = 'open'
    AWAITING_FINANCE_REVIEW = 'awaiting_finance_review'
    ADDRESSED = 'addressed'
    CLOSED = 'closed'

# Product/Variant Availability
class AvailabilityStatus(Enum):
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    DISCONTINUED = 'discontinued'

# Shipment Item
class ShipmentItemStatus(Enum):
    PENDING = 'pending'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    RETURNED = 'returned'
    DAMAGED = 'damaged'

# Shipping Snapshot
class ShippingSnapshotStatus(Enum):
    COMPLETE = 'complete'
    PARTIAL = 'partial'
    FAILED = 'failed'

# Shipment Event
class ShipmentEventStatus(Enum):
    CREATED = 'created'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'
    FAILED = 'failed'

# Shipment
class ShipmentStatus(Enum):
    CREATED = 'created'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'
    RETURNED = 'returned'
    CANCELLED = 'cancelled'

# Shift Request
class ShiftRequestStatus(Enum):
    REQUESTED = 'requested'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'

# Employee PTO/SickDay
class PTOStatus(Enum):
    REQUESTED = 'requested'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    TAKEN = 'taken'

# Employee Payment
class EmployeePaymentStatus(Enum):
    PENDING = 'pending'
    PROCESSED = 'processed'
    PAID = 'paid'
