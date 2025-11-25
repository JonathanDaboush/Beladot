from typing import Any, Optional
from datetime import datetime, timezone

class Payment:
    def __init__(self, id, order_id, amount_cents, method, status, transaction_id, raw_response, created_at, updated_at):
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