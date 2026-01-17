


"""
shippingServices.py

Service layer for shipment operations, including shipment events, issues, and item management.
All repository and model operations use a db session that is request-scoped and managed by the caller (not global).
"""
from backend.repositories.repository.shipment_repository import ShipmentRepository
from backend.persistance.shipment import Shipment
from backend.persistance.order import Order
from backend.repositories.repository.order_item_repository import OrderItemRepository
from backend.persistance.order_item import OrderItem
from backend.repositories.repository.shipment_item_repository import ShipmentItemRepository
from backend.persistance.shipment_item import ShipmentItem
from backend.persistance.shipment_event import ShipmentEvent
from backend.repositories.repository.shipment_event_repository import ShipmentEventRepository
from backend.persistance.shipment_issue import ShipmentIssue
from backend.repositories.repository.shipment_issue_repository import ShipmentIssueRepository
    # ...existing code...
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession


async def delete_shipment_issue(db: AsyncSession, issue_id: int):
    """
    Delete a shipment issue by its ID.
    Args:
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
        issue_id: ID of the shipment issue to delete.
    Returns:
        True if deleted, False otherwise.
    """
    """
    Delete a shipment issue by its ID.
    Args:
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
        issue_id: ID of the shipment issue to delete.
    Returns:
        True if deleted, False otherwise.
    """
    shipment_issue_repo = ShipmentIssueRepository(db)
    issue = await shipment_issue_repo.get_by_id(issue_id)
    if not issue:
        return False
    await db.delete(issue)
    await db.commit()
    return True

async def create_shipment_event(db: AsyncSession, shipment_id: int, status: str, description: str, location: str, occurred_at: datetime):
    """
    Create a shipment event for a shipment.
    Args:
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
        shipment_id: ID of the shipment.
        status: Status of the event.
        description: Description of the event.
        location: Location of the event.
        occurred_at: Datetime when the event occurred.
    Returns:
        The created ShipmentEvent object.
    """
    """
    Create a shipment event for a shipment.
    Args:
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
        shipment_id: ID of the shipment.
        status: Status of the event.
        description: Description of the event.
        location: Location of the event.
        occurred_at: Datetime when the event occurred.
    Returns:
        The created ShipmentEvent object.
    """
    shipment_event_repo = ShipmentEventRepository(db)
    from datetime import datetime
    now = datetime.utcnow()
    shipment_event = ShipmentEvent(
        event_id=None,  # PK is auto-generated
        shipment_id=shipment_id,
        status=status,
        description=description,
        location=location,
        occurred_at=occurred_at,
        created_at=now,
        updated_at=now
    )
    return await shipment_event_repo.save(shipment_event)

async def create_shipment_issue(db: AsyncSession, shipment_id: int, shipment_employee_name: str, issue_type: str, description: str, created_at: datetime, appointted_to: str):
    """
    Create a shipment issue for a shipment.
    Args:
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
        shipment_id: ID of the shipment.
        shipment_employee_name: Name of employee assigned.
        issue_type: Type of issue.
        description: Description of the issue.
        created_at: Datetime when the issue was created.
        appointted_to: Who the issue is appointed to.
    Returns:
        The created ShipmentIssue object.
    """
    shipment_issue_repo = ShipmentIssueRepository(db)
    shipment_issue = ShipmentIssue(
        issue_id=None,  # PK is auto-generated
        shipment_id=shipment_id,
        shipment_employee_name=shipment_employee_name,
        issue_type=issue_type,
        description=description,
        created_at=created_at,
        appointted_to=appointted_to
    )
    return await shipment_issue_repo.save(shipment_issue)
        # employee_id should be passed explicitly as a parameter
    """
    Create a shipment using order_id and other necessary info (except shipment_id).
    Args:
        order_id: The ID of the order to ship.
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
        shipment_status: Status of the shipment (e.g., 'pending', 'shipped').
        shipped_at: Optional datetime when shipped.
        delivered_at: Optional datetime when delivered.
    Returns:
        The created Shipment object.
    """
    from backend.models.model.enums import ShipmentStatus
    shipment_repo = ShipmentRepository(db)
    from datetime import datetime
    created_at = datetime.utcnow()
    updated_at = created_at
    # Only allow creation in CREATED state
    # Accept both enum and string for shipment_status
    if isinstance(shipment_status, str):
        status_val = shipment_status.lower()
    else:
        status_val = shipment_status.value.lower()
    if status_val != ShipmentStatus.CREATED.value:
        raise Exception('Shipment can only be created in CREATED state')
    shipment = Shipment(
        shipment_id=None,  # PK is auto-generated
        order_id=order_id,
        shipment_status=shipment_status
    )
    shipment = await shipment_repo.save(shipment)

    # Create ShipmentItems for each OrderItem in the order
    order_item_repo = OrderItemRepository(db)
    shipment_item_repo = ShipmentItemRepository(db)
    order_items = await order_item_repo.get_by_order_id(order_id)
    shipment_items = [
        ShipmentItem(
            shipment_item_id=None,
            shipment_id=shipment.shipment_id,
            product_id=item.product_id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            subtotal=item.subtotal
        ) for item in order_items
    ]
    for item in shipment_items:
        db.add(item)
    await db.commit()
    return shipment
async def get_shipments(shipment_id: int, db: AsyncSession):
    """
    Args:
        shipment_id: ID of the shipment.
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
    """
    # Read-only, but if mutation is allowed elsewhere, enforce transitions there
    shipment_repo = ShipmentRepository(db)
    shipment = await shipment_repo.get_by_id(shipment_id)
    return shipment

from sqlalchemy import select
async def get_shipment_details(shipment_id: int, db: AsyncSession):
    """
    Retrieve shipment details: shipment, shipment items, shipment events, and shipment issues.
    Args:
        shipment_id: ID of the shipment.
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
    """
    shipment_repo = ShipmentRepository(db)
    shipment_item_repo = ShipmentItemRepository(db)
    # Import event and issue models and repositories
    
    shipment_event_repo = ShipmentEventRepository(db)
    shipment_issue_repo = ShipmentIssueRepository(db)

    shipment = await shipment_repo.get_by_id(shipment_id)
    items_result = await db.execute(select(ShipmentItem).filter(ShipmentItem.shipment_id == shipment_id))
    shipment_items = items_result.scalars().all()
    events_result = await db.execute(select(ShipmentEvent).filter(ShipmentEvent.shipment_id == shipment_id))
    shipment_events = events_result.scalars().all()
    issues_result = await db.execute(select(ShipmentIssue).filter(ShipmentIssue.shipment_id == shipment_id))
    shipment_issues = issues_result.scalars().all()
    return {
        'shipment': shipment,
        'shipment_items': shipment_items,
        'shipment_events': shipment_events,
        'shipment_issues': shipment_issues
    }

async def edit_shipment_items(shipment_id: int, db: AsyncSession, items_data):
    """
    Edit shipment items for a shipment.
    Args:
        shipment_id: ID of the shipment.
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
        items_data: list of dicts with keys matching ShipmentItem fields.
    items_data: list of dicts with keys matching ShipmentItem fields (including shipment_item_id for update, and optionally shipment_event_id)
    """
    from backend.models.model.enums import ShipmentItemStatus
    shipment_item_repo = ShipmentItemRepository(db)
    # Collect all IDs to fetch in one query
    id_to_item = {item.get('shipment_item_id'): item for item in items_data if item.get('shipment_item_id')}
    if not id_to_item:
        return True
    # Fetch all current items in one batch
    current_items_result = await db.execute(select(ShipmentItem).filter(ShipmentItem.shipment_item_id.in_(list(id_to_item.keys()))))
    current_items = current_items_result.scalars().all()
    # Validate and prepare updates
    updates = []
    for current in current_items:
        item = id_to_item.get(current.shipment_item_id)
        if not item:
            continue
        terminal_states = [ShipmentItemStatus.DELIVERED, ShipmentItemStatus.RETURNED, ShipmentItemStatus.DAMAGED]
        if current.status in terminal_states:
            raise Exception(f'ShipmentItem {current.shipment_item_id} is immutable in terminal state: {current.status}')
        allowed = {
            ShipmentItemStatus.PENDING: [ShipmentItemStatus.SHIPPED, ShipmentItemStatus.DAMAGED],
            ShipmentItemStatus.SHIPPED: [ShipmentItemStatus.DELIVERED, ShipmentItemStatus.RETURNED, ShipmentItemStatus.DAMAGED],
        }
        new_status = item.get('status', current.status)
        if current.status in allowed and new_status not in allowed[current.status]:
            raise Exception(f'Invalid state transition for ShipmentItem {current.shipment_item_id}: {current.status} -> {new_status}')
        updates.append((current.shipment_item_id, item))
    # Batch update
    for shipment_item_id, item in updates:
        await shipment_item_repo.update(shipment_item_id, **item)
    return True

async def edit_shipment_events(shipment_id: int, db: AsyncSession, events_data):
    """
    Edit shipment events for a shipment.
    Args:
        shipment_id: ID of the shipment.
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
        events_data: list of dicts with keys matching ShipmentEvent fields.
    events_data: list of dicts with keys matching ShipmentEvent fields (including event_id for update)
    """
    from backend.models.model.enums import ShipmentEventStatus
    shipment_event_repo = ShipmentEventRepository(db)
    id_to_event = {event.get('event_id'): event for event in events_data if event.get('event_id')}
    if not id_to_event:
        return True
    current_events_result = await db.execute(select(ShipmentEvent).filter(ShipmentEvent.event_id.in_(list(id_to_event.keys()))))
    current_events = current_events_result.scalars().all()
    updates = []
    for current in current_events:
        event = id_to_event.get(current.event_id)
        if not event:
            continue
        terminal_states = [ShipmentEventStatus.DELIVERED, ShipmentEventStatus.FAILED]
        if current.status in terminal_states:
            raise Exception(f'ShipmentEvent {current.event_id} is immutable in terminal state: {current.status}')
        allowed = {
            ShipmentEventStatus.CREATED: [ShipmentEventStatus.IN_TRANSIT, ShipmentEventStatus.FAILED],
            ShipmentEventStatus.IN_TRANSIT: [ShipmentEventStatus.DELIVERED, ShipmentEventStatus.FAILED],
        }
        new_status = event.get('status', current.status)
        if current.status in allowed and new_status not in allowed[current.status]:
            raise Exception(f'Invalid state transition for ShipmentEvent {current.event_id}: {current.status} -> {new_status}')
        updates.append((current.event_id, event))
    for event_id, event in updates:
        await shipment_event_repo.update(event_id, **event)
    return True

async def edit_shipment_issues(shipment_id: int, db: AsyncSession, issues_data):
    """
    Edit shipment issues for a shipment.
    Args:
        shipment_id: ID of the shipment.
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
        issues_data: list of dicts with keys matching ShipmentIssue fields.
    issues_data: list of dicts with keys matching ShipmentIssue fields (including issue_id for update)
    """
    shipment_issue_repo = ShipmentIssueRepository(db)
    id_to_issue = {issue.get('issue_id'): issue for issue in issues_data if issue.get('issue_id')}
    if not id_to_issue:
        return True
    current_issues_result = await db.execute(select(ShipmentIssue).filter(ShipmentIssue.issue_id.in_(list(id_to_issue.keys()))))
    current_issues = current_issues_result.scalars().all()
    for current in current_issues:
        issue = id_to_issue.get(current.issue_id)
        if issue:
            await shipment_issue_repo.update(current.issue_id, **issue)
    return True

async def get_shipment_event(event_id: int, db: AsyncSession):
    """
    Retrieve a shipment event by its ID.
    Args:
        event_id: ID of the shipment event.
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
    """
    shipment_event_repo = ShipmentEventRepository(db)
    return await shipment_event_repo.get_by_id(event_id)





