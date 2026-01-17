from backend.utilities.emailService import generate_email


"""
customerAssistanceServices.py

Service layer for customer assistance operations, including refunds, payouts,
email notifications, and shipment issue handling. All repository/model operations
use a request-scoped DB session managed by the caller.
"""

from backend.repositories.repository.sellers_expense_repository import SellerExpenseRepository
from backend.models.model.sellers_expense import SellerExpense
from backend.services.payout_utils import create_refund, create_seller_payout, create_reimbursement
from backend.repositories.repository.order_repository import OrderRepository
from backend.repositories.repository.refund_request_repository import RefundRequestRepository
from backend.models.model.order import Order
from backend.models.model.refund_request import RefundRequest
from backend.repositories.repository.order_item_repository import OrderItemRepository
from backend.repositories.repository.product_repository import ProductRepository
from backend.repositories.repository.product_variant_repository import ProductVariantRepository
from backend.repositories.repository.product_image_repository import ProductImageRepository
from backend.repositories.repository.product_variant_image_repository import ProductVariantImageRepository
from backend.models.model.order_item import OrderItem
from backend.repositories.repository.shipment_issue_repository import ShipmentIssueRepository
from backend.repositories.repository.shipment_repository import ShipmentRepository
from backend.repositories.repository.shipment_item_repository import ShipmentItemRepository
from backend.models.model.shipment_issue import ShipmentIssue
from backend.models.model.shipment import Shipment
from backend.models.model.shipment_item import ShipmentItem
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

def send_customer_refund_status_email(customer_email, customer_name, order_id, refund_amount, status, description=None):
    """
    Send an email to the customer about their refund request status (approved or denied), including the description if provided.
    Args:
        customer_email (str): Customer's email address.
        customer_name (str): Customer's name.
        order_id (int): Order identifier.
        refund_amount (float): Amount refunded.
        status (str): Refund status ('approved', 'denied', etc.).
        description (str, optional): Additional description for the refund status.
    """
    """
    Send an email to the customer about their refund request status (approved or denied), including the description if provided.
    Args:
        customer_email (str): Customer's email address.
        customer_name (str): Customer's name.
        order_id (int): Order identifier.
        refund_amount (float): Amount refunded.
        status (str): Refund status ('approved', 'denied', etc.).
        description (str, optional): Additional description for the refund status.
    """
    if str(status).lower() == 'approved':
        subject = "Your Refund Request Was Approved"
        status_message = "approved"
    elif str(status).lower() == 'denied':
        subject = "Your Refund Request Was Denied"
        status_message = "denied"
    else:
        subject = "Update on Your Refund Request"
        status_message = str(status)
    pagePath = os.path.join('emails', 'customer_refund_status.html')
    # Read and format the HTML template
    with open(os.path.join(os.path.dirname(__file__), '../htmlpages', pagePath), 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_content = html_content.replace('{{ customer_name }}', customer_name)
    html_content = html_content.replace('{{ order_id }}', str(order_id))
    html_content = html_content.replace('{{ refund_amount }}', str(refund_amount))
    html_content = html_content.replace('{{ status }}', status_message)
    if description is not None:
        html_content = html_content.replace('{{ description }}', description)
    else:
        html_content = html_content.replace('{{ description }}', '')
    return generate_email(customer_email, subject, pagePath)

# Email notification for seller if product is broken before shipment
def send_seller_broken_product_notification(seller_email, seller_name, product_name, order_id, quantity, variant_name=None):
    """
    Send an email to the seller if a product/variant is broken before shipment.
    """
    subject = "Product Return Required: Broken Product Before Shipment"
    pagePath = os.path.join('emails', 'seller_broken_product_notification.html')
    # Read and format the HTML template
    with open(os.path.join(os.path.dirname(__file__), '../htmlpages', pagePath), 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_content = html_content.replace('{{ seller_name }}', seller_name)
    html_content = html_content.replace('{{ product_name }}', product_name)
    html_content = html_content.replace('{{ order_id }}', str(order_id))
    html_content = html_content.replace('{{ quantity }}', str(quantity))
    if variant_name:
        html_content = html_content.replace('{{ variant_name }}', variant_name)
    else:
        html_content = html_content.replace('{% if variant_name %} (Variant: <strong>{{ variant_name }}</strong>){% endif %}', '')
        html_content = html_content.replace('{{ variant_name }}', '')
    return generate_email(seller_email, subject, pagePath)

async def get_all_customer_refund_requests(user_id, db: AsyncSession, min_date=None, max_date=None):
    """
    Retrieve all refund requests for a user, optionally filtered by date range.
    """
    stmt = select(RefundRequest).join(Order, RefundRequest.order_id == Order.order_id).filter(Order.user_id == user_id)
    if min_date:
        stmt = stmt.filter(RefundRequest.date_of_request >= min_date)
    if max_date:
        stmt = stmt.filter(RefundRequest.date_of_request <= max_date)
    res = await db.execute(stmt)
    return res.scalars().all()


async def get_specific_refund_request(refund_request_id, db: AsyncSession):
    """Retrieve detailed info for a specific refund request."""
    refund_repo = RefundRequestRepository(db)
    order_repo = OrderRepository(db)
    order_item_repo = OrderItemRepository(db)
    product_repo = ProductRepository(db)
    variant_repo = ProductVariantRepository(db)
    image_repo = ProductImageRepository(db)
    variant_image_repo = ProductVariantImageRepository(db)
    refund = await refund_repo.get_by_id(refund_request_id)
    if not refund:
        return None
    order_res = await order_repo.db.execute(select(Order).filter(Order.order_id == refund.order_id))
    order = order_res.scalars().first()
    order_items_res = await order_item_repo.db.execute(select(OrderItem).filter(OrderItem.order_id == refund.order_id))
    order_items = order_items_res.scalars().all()
    detailed_items = []
    for item in order_items:
        product = await product_repo.get_by_id(item.product_id)
        product_images = await image_repo.get_by_product_id(item.product_id)
        variant = None
        variant_images = []
        if item.variant_id:
            variant = await variant_repo.get_by_id(item.variant_id)
            variant_images = await variant_image_repo.get_by_variant_id(item.variant_id)
        detailed_items.append({
            'order_item': item,
            'product': product,
            'product_images': product_images,
            'variant': variant,
            'variant_images': variant_images
        })
    return {
        'refund_request': refund,
        'order': order,
        'order_items': detailed_items
    }

async def process_customer_complaint(refund_request_id, db: AsyncSession, description=None, **update_fields):
    """
    Update the RefundRequest object with new values.
    Args:
        refund_request_id: ID of the refund request to update.
        db: SQLAlchemy session.
        update_fields: Fields to update on the RefundRequest.
    Returns:
        The updated RefundRequest object, or None if not found.
    """
    from backend.models.model.enums import RefundRequestStatus
    from backend.models.model.refund_ledger import RefundLedger
    from backend.repositories.repository.refund_ledger_repository import RefundLedgerRepository
    refund_repo = RefundRequestRepository(db)
    ledger_repo = RefundLedgerRepository(db)
    refund = await refund_repo.get_by_id(refund_request_id)
    if not refund:
        return None
    # Enforce: can only process if pending, and only allow valid transitions
    terminal_states = [RefundRequestStatus.APPROVED, RefundRequestStatus.DENIED]
    if refund.status in terminal_states:
        raise Exception('Refund request is immutable in terminal state')
    allowed = {
        RefundRequestStatus.PENDING: [RefundRequestStatus.APPROVED, RefundRequestStatus.DENIED],
    }
    action = None
    new_status = None
    if update_fields.get('approve'):
        new_status = RefundRequestStatus.APPROVED
        action = 'approved'
    elif update_fields.get('reject'):
        new_status = RefundRequestStatus.DENIED
        action = 'rejected'
    else:
        raise Exception('Invalid refund action')
    if refund.status in allowed and new_status not in allowed[refund.status]:
        raise Exception(f'Invalid state transition for RefundRequest: {refund.status} -> {new_status}')
    refund.status = new_status
    if description is not None:
        refund.description = description
    await db.commit()
    # Ledger: append refund event
    ledger_entry = RefundLedger(refund_id=refund.refund_request_id, action=action, amount=getattr(refund, 'refund_amount', 0))
    await ledger_repo.save(ledger_entry)
    # Send email to customer if refund is approved or denied
    order_repo = OrderRepository(db)
    order = await order_repo.get_by_id(refund.order_id)
    customer_email = getattr(order, 'customer_email', None) if order else None
    customer_name = getattr(order, 'customer_name', 'Customer') if order else 'Customer'
    refund_amount = getattr(refund, 'refund_amount', '')
    status = getattr(refund, 'status', '')
    if customer_email:
        send_customer_refund_status_email(customer_email, customer_name, refund.order_id, refund_amount, status, refund.description)
    return refund

async def get_shipment_greivence_reports(user_id, db: AsyncSession, min_date=None, max_date=None):
    """
    Retrieve all shipment issues for a user, optionally filtered by date.
    """
    """
    Args:
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
    """
    # Build query joining ShipmentIssue with Shipment and filter by user
    stmt = select(ShipmentIssue).join(Shipment, ShipmentIssue.shipment_id == Shipment.shipment_id)
    if hasattr(Shipment, 'order_id'):
        stmt = stmt.join(Order, Shipment.order_id == Order.order_id).filter(Order.user_id == user_id)
    if min_date:
        stmt = stmt.filter(Shipment.created_at >= min_date)
    if max_date:
        stmt = stmt.filter(Shipment.created_at <= max_date)
    res = await db.execute(stmt)
    return res.scalars().all()

async def get_greivence_details(issue_id, db: AsyncSession):
    """
    Retrieve details for a specific shipment issue, including the issue, shipment, and shipment items.
    """
    """
    Args:
        db: SQLAlchemy session (request-scoped, not global; managed by caller).
    """
    issue_repo = ShipmentIssueRepository(db)
    shipment_repo = ShipmentRepository(db)
    shipment_item_repo = ShipmentItemRepository(db)
    issue = await issue_repo.get_by_id(issue_id)
    if not issue:
        return None
    shipment = await shipment_repo.get_by_id(issue.shipment_id)
    items_res = await db.execute(select(ShipmentItem).filter(ShipmentItem.shipment_id == shipment.shipment_id))
    shipment_items = items_res.scalars().all()
    # Include appointted_to in the returned issue details if needed
    return {
        'shipment_issue': issue,
        'shipment': shipment,
        'shipment_items': shipment_items,
        'appointted_to': getattr(issue, 'appointted_to', None)
    }

async def process_shipment_report(issue_id, db: AsyncSession, **update_fields):
    """
    Update the ShipmentIssue object with new values and handle business logic for logistics vs seller fault.
    Args:
        issue_id: ID of the shipment issue to update.
        db: SQLAlchemy session.
        update_fields: Fields to update on the ShipmentIssue.
    Returns:
        The updated ShipmentIssue object, or None if not found.
    """
    issue_repo = ShipmentIssueRepository(db)
    shipment_repo = ShipmentRepository(db)
    order_repo = OrderRepository(db)
    order_item_repo = OrderItemRepository(db)
    updated_issue = await issue_repo.update(issue_id, **update_fields)
    if not updated_issue:
        return None

    issue_type = str(getattr(updated_issue, 'issue_type', '')).lower()
    shipment = await shipment_repo.get_by_id(updated_issue.shipment_id)
    order_id = getattr(shipment, 'order_id', None) if shipment else None

    # Enforce: can only process if unresolved
    from backend.models.model.enums import ShipmentIssueResolution
    if getattr(updated_issue, 'resolution', ShipmentIssueResolution.UNRESOLVED) != ShipmentIssueResolution.UNRESOLVED:
        raise Exception('Shipment issue already processed')

    # Only one resolution allowed, mutually exclusive
    if issue_type in ['broken_no_arrival_seller_fault', 'seller_fault']:
        updated_issue.resolution = ShipmentIssueResolution.SELLER_FAULT
        seller_expense_repo = SellerExpenseRepository(db)
        amount_owed = -abs(float(update_fields.get('item_value', 0)))
        if order_id is not None and amount_owed != 0:
            expense = SellerExpense(order_id=order_id, amount=amount_owed)
            await seller_expense_repo.save(expense)
        seller_email = getattr(shipment, 'seller_email', None) if shipment else None
        seller_name = getattr(shipment, 'seller_name', 'Seller') if shipment else 'Seller'
        product_name = getattr(updated_issue, 'product_name', 'Product')
        quantity = getattr(updated_issue, 'quantity', '1')
        variant_name = getattr(updated_issue, 'variant_name', None)
        if seller_email:
            await send_seller_broken_product_notification(seller_email, seller_name, product_name, order_id, quantity, variant_name)
    elif issue_type in ['broken_at_shipment', 'shipment_fault', 'no_arrival_shipment_fault', 'shipment_lost']:
        updated_issue.resolution = ShipmentIssueResolution.SHIPMENT_FAULT
        seller_expense_repo = SellerExpenseRepository(db)
        amount_given = abs(float(update_fields.get('item_value', 0)))
        if order_id is not None and amount_given != 0:
            expense = SellerExpense(order_id=order_id, amount=amount_given)
            await seller_expense_repo.save(expense)
        seller_email = getattr(shipment, 'seller_email', None) if shipment else None
        seller_name = getattr(shipment, 'seller_name', 'Seller') if shipment else 'Seller'
        product_name = getattr(updated_issue, 'product_name', 'Product')
        quantity = getattr(updated_issue, 'quantity', '1')
        variant_name = getattr(updated_issue, 'variant_name', None)
        if seller_email:
            await send_seller_broken_product_notification(seller_email, seller_name, product_name, order_id, quantity, variant_name)
    else:
        updated_issue.resolution = ShipmentIssueResolution.UNRESOLVED
    await db.commit()
    return updated_issue
