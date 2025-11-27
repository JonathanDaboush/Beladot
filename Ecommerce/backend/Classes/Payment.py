from typing import Any, Optional
from datetime import datetime, timezone

class Payment:
    """
    Domain model representing a payment transaction with gateway integration.
    
    This class manages payment lifecycle including authorization, capture, refunds,
    and voids. It integrates with payment gateways (Stripe, PayPal, etc.) and tracks
    the full payment state.
    
    Key Responsibilities:
        - Store payment transaction details (amount, method, status)
        - Coordinate with payment gateway for capture/refund/void operations
        - Track payment state (pending, authorized, completed, refunded, failed)
        - Preserve gateway responses for reconciliation and debugging
        - Support partial refunds
    
    Payment Flow:
        1. Authorization: Gateway authorizes amount (status: authorized)
        2. Capture: Funds actually captured (status: completed)
        3. Refund: Funds returned to customer (status: refunded/partially_refunded)
        4. Void: Authorization cancelled before capture
    
    Security Considerations:
        - Card details NEVER stored (PCI compliance)
        - Gateway handles all sensitive data
        - raw_response may contain sensitive data (access control required)
    
    Design Notes:
        - Prices stored in cents (avoids floating-point errors)
        - transaction_id links to gateway transaction
        - raw_response enables debugging and reconciliation
        - This is a domain object; persistence handled by PaymentRepository
    """
    def __init__(self, id, order_id, amount_cents, method, status, transaction_id, raw_response, created_at, updated_at):
        """
        Initialize a Payment domain object.
        
        Args:
            id: Unique identifier (None for new payments before persistence)
            order_id: Foreign key to the order
            amount_cents: Payment amount in cents
            method: Payment method (e.g., 'credit_card', 'paypal', 'bank_transfer')
            status: Payment status (pending, authorized, completed, refunded, failed)
            transaction_id: Gateway transaction identifier
            raw_response: Full gateway response dictionary (for debugging/reconciliation)
            created_at: Payment creation timestamp
            updated_at: Last modification timestamp
        """
        self.id = id
        self.order_id = order_id
        self.amount_cents = amount_cents
        self.method = method
        self.status = status
        self.transaction_id = transaction_id
        self.raw_response = raw_response
        self.created_at = created_at
        self.updated_at = updated_at
    
    def capture(self, amount_cents: Optional[int], payment_gateway, repository) -> dict[str, Any]:
        """
        Capture a previously authorized payment.
        
        Args:
            amount_cents: Amount to capture (None means capture full amount)
            payment_gateway: Gateway service for processing capture
            repository: Repository for persisting state changes (optional)
            
        Returns:
            dict: Result with 'success' (bool), 'amount_cents', 'transaction_id',
                  and 'error' on failure
                  
        Capture Rules:
            - Cannot capture already completed payment (idempotent)
            - Capture amount cannot exceed authorized amount
            - Requires payment gateway
            
        Side Effects:
            - Changes status to 'completed' on success or 'failed' on error
            - Updates raw_response with gateway response
            - Updates updated_at timestamp
            - Persists payment via repository
            
        Design Notes:
            - Idempotent (returns success if already captured)
            - Supports partial capture (amount_cents < authorized amount)
            - Gateway errors captured in raw_response for debugging
        """
        if self.status == "completed":
            return {
                "success": True,
                "message": "Payment already captured",
                "amount_cents": self.amount_cents,
                "transaction_id": self.transaction_id
            }
        
        capture_amount = amount_cents if amount_cents is not None else self.amount_cents
        
        if capture_amount > self.amount_cents:
            return {
                "success": False,
                "error": f"Capture amount {capture_amount} exceeds authorized amount {self.amount_cents}"
            }
        
        if payment_gateway:
            try:
                gateway_response = payment_gateway.capture_payment(self.transaction_id, capture_amount)
                
                if gateway_response.get("success"):
                    self.status = "completed"
                    self.raw_response = gateway_response
                    self.updated_at = datetime.now(timezone.utc)
                    
                    if repository:
                        repository.update(self)
                    
                    return {
                        "success": True,
                        "amount_cents": capture_amount,
                        "transaction_id": self.transaction_id,
                        "gateway_response": gateway_response
                    }
                else:
                    self.status = "failed"
                    self.raw_response = gateway_response
                    self.updated_at = datetime.now(timezone.utc)
                    
                    if repository:
                        repository.update(self)
                    
                    return {
                        "success": False,
                        "error": gateway_response.get("error", "Capture failed")
                    }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Payment gateway not available"}
    
    def refund(self, amount_cents: int, payment_gateway, repository) -> dict[str, Any]:
        """
        Refund a completed payment (full or partial).
        
        Args:
            amount_cents: Amount to refund in cents (must be positive)
            payment_gateway: Gateway service for processing refund
            repository: Repository for persisting state changes (optional)
            
        Returns:
            dict: Result with 'success' (bool), 'amount_cents', 'transaction_id',
                  and 'error' on failure
                  
        Refund Rules:
            - Can only refund completed payments
            - Amount must be positive and not exceed payment amount
            - Requires payment gateway
            
        Side Effects:
            - Changes status to 'refunded' (full) or 'partially_refunded' (partial)
            - Updates updated_at timestamp
            - Persists payment via repository
            
        Design Notes:
            - Gateway refund_id returned in transaction_id field
            - Multiple partial refunds supported (track total elsewhere)
            - Gateway errors returned in result dictionary
        """
        if self.status != "completed":
            return {"success": False, "error": "Can only refund completed payments"}
        
        if amount_cents <= 0 or amount_cents > self.amount_cents:
            return {"success": False, "error": "Invalid refund amount"}
        
        if payment_gateway:
            try:
                gateway_response = payment_gateway.refund_payment(self.transaction_id, amount_cents)
                
                if gateway_response.get("success"):
                    self.status = "refunded" if amount_cents >= self.amount_cents else "partially_refunded"
                    self.updated_at = datetime.now(timezone.utc)
                    
                    if repository:
                        repository.update(self)
                    
                    return {
                        "success": True,
                        "amount_cents": amount_cents,
                        "transaction_id": gateway_response.get("refund_id"),
                        "gateway_response": gateway_response
                    }
                else:
                    return {"success": False, "error": gateway_response.get("error", "Refund failed")}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Payment gateway not available"}
    
    def void(self, payment_gateway, repository) -> dict[str, Any]:
        """
        Void an authorized but not yet captured payment.
        
        Args:
            payment_gateway: Gateway service for processing void
            repository: Repository for persisting state changes (optional)
            
        Returns:
            dict: Result with 'success' (bool), 'transaction_id', and 'error' on failure
            
        Void Rules:
            - Can only void pending or authorized payments (not captured)
            - Requires payment gateway
            
        Side Effects:
            - Changes status to 'cancelled'
            - Updates updated_at timestamp
            - Persists payment via repository
            
        Design Notes:
            - Void cancels authorization before funds are captured
            - Different from refund (which returns captured funds)
            - Gateway errors returned in result dictionary
        """
        if self.status not in ["pending", "authorized"]:
            return {"success": False, "error": "Can only void pending or authorized payments"}
        
        if payment_gateway:
            try:
                gateway_response = payment_gateway.void_payment(self.transaction_id)
                
                if gateway_response.get("success"):
                    self.status = "cancelled"
                    self.updated_at = datetime.now(timezone.utc)
                    
                    if repository:
                        repository.update(self)
                    
                    return {
                        "success": True,
                        "transaction_id": self.transaction_id,
                        "gateway_response": gateway_response
                    }
                else:
                    return {"success": False, "error": gateway_response.get("error", "Void failed")}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Payment gateway not available"}