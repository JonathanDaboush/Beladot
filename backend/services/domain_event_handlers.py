"""
domain_event_handlers.py

Event handler functions for domain events, such as refund approval and denial.
Handles updating refund status and logging actions in the refund ledger.
All operations are asynchronous and require a database session.
"""

from backend.models.model.domain_event import DomainEvent, DomainEventType
from backend.models.model.enums import RefundRequestStatus
from backend.models.model.refund_ledger import RefundLedger
from backend.repositories.repository.refund_ledger_repository import RefundLedgerRepository
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

async def handle_refund_event(event: DomainEvent, db: AsyncSession) -> Optional[object]:
    """
    Handle refund-related domain events (approval/denial).
    Updates refund status and logs the action in the refund ledger.
    Args:
        event: DomainEvent instance
        db: Database session
    Returns:
        Updated Refund object
    Raises:
        Exception if refund not found or already processed, or event type invalid
    """
    from backend.repositories.repository.refund_request_repository import RefundRequestRepository
    refund_repo = RefundRequestRepository(db)
    ledger_repo = RefundLedgerRepository(db)
    refund = await refund_repo.get_by_id(event.entity_id)
    if not refund:
        raise Exception('Refund request not found')
    # Only allow if pending
    if refund.status != RefundRequestStatus.PENDING:
        raise Exception('Refund request already processed')
    if event.event_type == DomainEventType.REFUND_APPROVED:
        refund.status = RefundRequestStatus.APPROVED
        action = 'approved'
    elif event.event_type == DomainEventType.REFUND_DENIED:
        refund.status = RefundRequestStatus.DENIED
        action = 'rejected'
    else:
        raise Exception('Invalid refund event type')
    if 'description' in event.payload:
        refund.description = event.payload['description']
    await db.commit()
    ledger_entry = RefundLedger(refund_id=refund.refund_request_id, action=action, amount=getattr(refund, 'refund_amount', 0))
    await ledger_repo.save(ledger_entry)
    # Optionally emit notifications here
    return refund
