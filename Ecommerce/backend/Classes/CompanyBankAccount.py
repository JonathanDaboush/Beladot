from datetime import datetime

class CompanyBankAccount:
    def __init__(self, id, account_number, routing_number, bank_name, account_holder_name, created_at, updated_at):
        self.id = id
        self.account_number = account_number
        self.routing_number = routing_number
        self.bank_name = bank_name
        self.account_holder_name = account_holder_name
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'account_number': self.account_number,
            'routing_number': self.routing_number,
            'bank_name': self.bank_name,
            'account_holder_name': self.account_holder_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
