from typing import Optional
from datetime import datetime, timezone

class Seller:
    def __init__(self, id, user_id, legal_business_name, business_type, phone_number, business_address, tax_id, tax_country, is_verified, verification_submitted_at, verified_at, created_at, updated_at, finance_info=None, payouts=None):
        self.id = id
        self.user_id = user_id
        self.legal_business_name = legal_business_name
        self.business_type = business_type
        self.phone_number = phone_number
        self.business_address = business_address
        self.tax_id = tax_id
        self.tax_country = tax_country
        self.is_verified = is_verified
        self.verification_submitted_at = verification_submitted_at
        self.verified_at = verified_at
        self.created_at = created_at
        self.updated_at = updated_at
        self.finance_info = finance_info
        self.payouts = payouts or []
