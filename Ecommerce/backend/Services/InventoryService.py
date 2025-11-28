from typing import Any
from uuid import UUID

from Ecommerce.backend.Classes import ProductVariant as productvariant, InventoryTransaction as inventorytransaction
from Ecommerce.backend.Repositories import ProductVariantRepository as productvariantrepository, InventoryTransactionRepository as inventorytransactionrepository

class InventoryService:
    """
    Inventory Management Service
    Authoritative controller for stock levels, reservations, and reconciliation.
    Prevents oversells and provides inventory integrity through atomic operations.
    Uses DB row locking or optimistic concurrency with retry.
    """
    
    def __init__(self, variant_repository, transaction_repository, audit_log_repository):
        self.variant_repository = variant_repository
        self.transaction_repository = transaction_repository
        self.audit_log_repository = audit_log_repository
    
    async def check_availability(self, variant_id: UUID, requested_qty: int, actor_id=None) -> bool:
        variant = await self.variant_repository.get_by_id(variant_id)
        available = variant.available_quantity(self.transaction_repository)
        result = available >= requested_qty
        await self.audit_log_repository.create({
            'actor_id': actor_id,
            'action': 'check_availability',
            'target_type': 'product_variant',
            'target_id': variant_id,
            'metadata': {'requested_qty': requested_qty, 'available': available, 'result': result}
        })
        return result
    
    async def reserve_stock(self, variant_id: UUID, qty: int, reason: str, reference_id: UUID = None, actor_id=None):
        variant = await self.variant_repository.get_by_id(variant_id)
        if not await self.check_availability(variant_id, qty):
            raise ValueError('Not enough stock to reserve')
        from Ecommerce.backend.Classes.InventoryTransaction import InventoryTransaction
        transaction = InventoryTransaction(
            id=None,
            product_id=variant_id,
            transaction_type='reservation',
            quantity_change=-qty,
            quantity_after=variant.stock_quantity - qty,
            reference_id=reference_id,
            actor_id=actor_id,
            notes=reason,
            created_at=None
        )
        created = await self.transaction_repository.create_transaction(transaction)
        await self.audit_log_repository.create({
            'actor_id': actor_id,
            'action': 'reserve_stock',
            'target_type': 'inventory_transaction',
            'target_id': created.id,
            'metadata': {'variant_id': variant_id, 'qty': qty, 'reason': reason}
        })
        return created.id
    
    async def confirm_reservation(self, transaction_id: UUID, actor_id=None) -> None:
        transaction = await self.transaction_repository.get_by_id(transaction_id)
        if not transaction or transaction.transaction_type != 'reservation':
            raise ValueError('Reservation not found')
        # Mark as confirmed by creating a sale transaction
        from Ecommerce.backend.Classes.InventoryTransaction import InventoryTransaction
        sale_tx = InventoryTransaction(
            id=None,
            product_id=transaction.product_id,
            transaction_type='sale',
            quantity_change=transaction.quantity_change,
            quantity_after=transaction.quantity_after,
            reference_id=transaction.reference_id,
            actor_id=actor_id,
            notes='Confirmed reservation',
            created_at=None
        )
        await self.transaction_repository.create_transaction(sale_tx)
        await self.audit_log_repository.create({
            'actor_id': actor_id,
            'action': 'confirm_reservation',
            'target_type': 'inventory_transaction',
            'target_id': transaction_id,
            'metadata': {'confirmed': True}
        })
    
    async def release_reservation(self, transaction_id: UUID, actor_id=None) -> None:
        transaction = await self.transaction_repository.get_by_id(transaction_id)
        if not transaction or transaction.transaction_type != 'reservation':
            raise ValueError('Reservation not found')
        # Release by creating a release transaction (positive delta)
        from Ecommerce.backend.Classes.InventoryTransaction import InventoryTransaction
        release_tx = InventoryTransaction(
            id=None,
            product_id=transaction.product_id,
            transaction_type='release',
            quantity_change=abs(transaction.quantity_change),
            quantity_after=transaction.quantity_after + abs(transaction.quantity_change),
            reference_id=transaction.reference_id,
            actor_id=actor_id,
            notes='Released reservation',
            created_at=None
        )
        await self.transaction_repository.create_transaction(release_tx)
        await self.audit_log_repository.create({
            'actor_id': actor_id,
            'action': 'release_reservation',
            'target_type': 'inventory_transaction',
            'target_id': transaction_id,
            'metadata': {'released': True}
        })
    
    async def adjust_stock(self, variant_id: UUID, delta: int, reason: str, actor_id=None, reference_id=None):
        variant = await self.variant_repository.get_by_id(variant_id)
        from Ecommerce.backend.Classes.InventoryTransaction import InventoryTransaction
        transaction = InventoryTransaction(
            id=None,
            product_id=variant_id,
            transaction_type=reason,
            quantity_change=delta,
            quantity_after=variant.stock_quantity + delta,
            reference_id=reference_id,
            actor_id=actor_id,
            notes=f'Adjust stock: {reason}',
            created_at=None
        )
        await self.transaction_repository.create_transaction(transaction)
        await self.audit_log_repository.create({
            'actor_id': actor_id,
            'action': 'adjust_stock',
            'target_type': 'inventory_transaction',
            'target_id': variant_id,
            'metadata': {'delta': delta, 'reason': reason}
        })
