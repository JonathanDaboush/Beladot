from datetime import datetime

class SellerPayout:
    def __init__(self, id, seller_id, amount, payout_date, status, related_order_ids, created_at, updated_at):
        self.id = id
        self.seller_id = seller_id
        self.amount = amount
        self.payout_date = payout_date
        self.status = status
        self.related_order_ids = related_order_ids  # list or CSV
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'amount': float(self.amount),
            'payout_date': self.payout_date.isoformat() if self.payout_date else None,
            'status': self.status,
            'related_order_ids': self.related_order_ids,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
