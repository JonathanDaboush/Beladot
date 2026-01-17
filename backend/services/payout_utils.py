from backend.persistance.refund import Refund
from backend.persistance.seller_payout import SellerPayout
from backend.persistance.reimbursement import Reimbursement
from backend.repositories.repository.refund_repository import RefundRepository
from backend.repositories.repository.seller_payout_repository import SellerPayoutRepository
from backend.repositories.repository.reimbursement_repository import ReimbursementRepository
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

async def create_refund(db: AsyncSession, payment_id: int, order_item_id: int, amount: float, reason: str, approved_by_cs_id: int, status: str) -> Refund:
    """
    Create a refund record and save it to the database.
    Args:
        db: Database session
        payment_id: Payment ID
        order_item_id: Order item ID
        amount: Refund amount
        reason: Reason for refund
        approved_by_cs_id: Customer service approver ID
        status: Refund status
    Returns:
        Saved Refund object
    """
    refund = Refund(
        refund_id=None,  # Assume autoincrement
        payment_id=payment_id,
        order_item_id=order_item_id,
        amount=amount,
        reason=reason,
        approved_by_cs_id=approved_by_cs_id,
        status=status,
        created_at=datetime.now(),
        processed_at=None
    )
    repo = RefundRepository(db)
    return await repo.save(refund)
async def create_seller_payout(db: AsyncSession, seller_id: int, amount: float, currency: str, status: str = 'pending') -> SellerPayout:
    """
    Create a seller payout record and save it to the database.
    Args:
                db: Database session
                seller_id: Seller ID
                amount: Payout amount
                currency: Currency code
                status: Payout status (default 'pending')
            Returns:
                Saved SellerPayout object
            """
    payout = SellerPayout(
        payout_id=None,  # Assume autoincrement
        seller_id=seller_id,
        amount=amount,
        currency=currency,
        date_of_payment=None,
        status=status,
        created_at=datetime.now()
    )
async def create_reimbursement(db: AsyncSession, employee_id: int, incident_id: int, description: str, amount_approved: float, status: bool = True) -> Reimbursement:
    """
    Create a reimbursement record and save it to the database.
    Args:
        db: Database session
        employee_id: Employee ID
                incident_id: Incident ID
                description: Description of reimbursement
                amount_approved: Approved amount
                status: Reimbursement status (default True)
            Returns:
                Saved Reimbursement object
            """
    reimbursement = Reimbursement(
        reimbursement_id=None,  # Assume autoincrement
        employee_id=employee_id,
        incident_id=incident_id,
        description=description,
        response=None,
        amount_approved=amount_approved,
        status=status,
        status_addressed=True,
        paid_all=False
    )
    repo = ReimbursementRepository(db)
    return await repo.save(reimbursement)
