from backend.model.enums import EmployeePaymentStatus

class EmployeePayment:
    def __init__(self, payment_id, emp_id, amount, payment_type, status=EmployeePaymentStatus.PENDING, processed_by_finance_emp_id=None, created_at=None, paid_at=None):
        self.payment_id = payment_id
        self.emp_id = emp_id
        self.amount = amount
        self.payment_type = payment_type
        self.status = status
        self.processed_by_finance_emp_id = processed_by_finance_emp_id
        self.created_at = created_at
        self.paid_at = paid_at
