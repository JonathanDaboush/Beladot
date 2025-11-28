from typing import Optional
from datetime import datetime, timezone

class SellerFinance:
    def __init__(self, id, seller_id, bank_account_number, bank_routing_number, account_holder_name, bank_country, payout_frequency, document_type, document_url, document_verified, created_at, updated_at):
        self.id = id
        self.seller_id = seller_id
        self.bank_account_number = bank_account_number
        self.bank_routing_number = bank_routing_number
        self.account_holder_name = account_holder_name
        self.bank_country = bank_country
        self.payout_frequency = payout_frequency
        self.document_type = document_type
        self.document_url = document_url
        self.document_verified = document_verified
        self.created_at = created_at
        self.updated_at = updated_at
