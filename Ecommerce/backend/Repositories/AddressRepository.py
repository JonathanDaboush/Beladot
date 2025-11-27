from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Address import Address
from typing import List


class AddressRepository:
    """
    Data access layer for Address entities.
    
    This repository handles address persistence and queries, supporting
    address book functionality for users with multiple saved addresses.
    
    Responsibilities:
        - Address CRUD operations
        - Query addresses by user
        - Support address validation and verification
    
    Design Patterns:
        - Repository Pattern: Isolates address data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = AddressRepository(db_session)
        addresses = await repository.get_by_user(user_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Address
    
    async def get_by_id(self, address_id: int) -> Address:
        """
        Retrieve an address by its unique identifier.
        
        Args:
            address_id: The unique ID of the address
            
        Returns:
            Address: The address object if found, None otherwise
        """
        result = await self.db.execute(select(Address).where(Address.id == address_id))
        return result.scalar_one_or_none()
    
    async def get_by_user(self, user_id: int) -> List[Address]:
        """
        Retrieve all addresses belonging to a specific user.
        
        Args:
            user_id: The user ID to find addresses for
            
        Returns:
            List[Address]: List of address objects for the user
            
        Use Case:
            Populate address book or address selector during checkout
        """
        result = await self.db.execute(
            select(Address).where(Address.user_id == user_id)
        )
        return result.scalars().all()
    
    async def create(self, address: Address) -> Address:
        """
        Create a new address record.
        
        Args:
            address: Address object to persist
            
        Returns:
            Address: Created address with database-generated ID
            
        Side Effects:
            - Commits transaction immediately
            - Sets timestamps via database defaults
        """
        self.db.add(address)
        await self.db.commit()
        await self.db.refresh(address)
        return address
    
    async def update(self, address: Address):
        """
        Update an existing address.
        
        Args:
            address: Address object with modifications
            
        Side Effects:
            - Updates address.updated_at
            - Commits transaction immediately
        """
        await self.db.merge(address)
        await self.db.commit()
        await self.db.refresh(address)
    
    async def delete(self, address_id: int):
        """
        Delete an address from the database.
        
        Args:
            address_id: ID of the address to delete
            
        Side Effects:
            - Permanently removes address
            - Commits transaction immediately
            
        Note:
            Address must not be referenced by any orders
        """
        address = await self.get_by_id(address_id)
        if address:
            await self.db.delete(address)
            await self.db.commit()
