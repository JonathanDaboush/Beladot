"""
Shift Swap Repository

Data access for shift trade/swap requests.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from Models.ShiftSwap import ShiftSwap, SwapStatus
from typing import Optional, List
from datetime import datetime


class ShiftSwapRepository:
    """Repository for shift swap operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, swap: ShiftSwap) -> ShiftSwap:
        """Create a new shift swap request."""
        swap.created_at = datetime.now()
        swap.updated_at = datetime.now()
        
        self.session.add(swap)
        await self.session.commit()
        await self.session.refresh(swap)
        
        return swap
    
    async def get_by_id(self, swap_id: int) -> Optional[ShiftSwap]:
        """Get swap request by ID."""
        result = await self.session.execute(
            select(ShiftSwap).where(ShiftSwap.id == swap_id)
        )
        return result.scalar_one_or_none()
    
    async def get_pending_for_employee(
        self,
        employee_id: int
    ) -> List[ShiftSwap]:
        """Get pending swap requests targeting an employee."""
        result = await self.session.execute(
            select(ShiftSwap).where(
                and_(
                    ShiftSwap.target_employee_id == employee_id,
                    ShiftSwap.status == SwapStatus.PENDING
                )
            ).order_by(ShiftSwap.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_requesting_employee(
        self,
        employee_id: int
    ) -> List[ShiftSwap]:
        """Get all swap requests made by an employee."""
        result = await self.session.execute(
            select(ShiftSwap).where(
                ShiftSwap.requesting_employee_id == employee_id
            ).order_by(ShiftSwap.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_pending_manager_approval(
        self,
        manager_id: int = None
    ) -> List[ShiftSwap]:
        """Get swap requests pending manager approval."""
        result = await self.session.execute(
            select(ShiftSwap).where(
                ShiftSwap.status == SwapStatus.ACCEPTED_BY_EMPLOYEE
            ).order_by(ShiftSwap.created_at)
        )
        return result.scalars().all()
    
    async def accept_by_employee(self, swap_id: int) -> Optional[ShiftSwap]:
        """Target employee accepts the swap."""
        swap = await self.get_by_id(swap_id)
        if not swap:
            return None
        
        swap.status = SwapStatus.ACCEPTED_BY_EMPLOYEE
        swap.accepted_at = datetime.now()
        swap.updated_at = datetime.now()
        
        await self.session.commit()
        await self.session.refresh(swap)
        
        return swap
    
    async def approve_by_manager(
        self,
        swap_id: int,
        manager_id: int,
        notes: str = None
    ) -> Optional[ShiftSwap]:
        """Manager approves the swap."""
        swap = await self.get_by_id(swap_id)
        if not swap:
            return None
        
        swap.status = SwapStatus.APPROVED
        swap.approved_by = manager_id
        swap.approved_at = datetime.now()
        swap.manager_notes = notes
        swap.updated_at = datetime.now()
        
        await self.session.commit()
        await self.session.refresh(swap)
        
        return swap
    
    async def deny(
        self,
        swap_id: int,
        manager_id: int,
        reason: str
    ) -> Optional[ShiftSwap]:
        """Deny swap request."""
        swap = await self.get_by_id(swap_id)
        if not swap:
            return None
        
        swap.status = SwapStatus.DENIED
        swap.approved_by = manager_id
        swap.denial_reason = reason
        swap.updated_at = datetime.now()
        
        await self.session.commit()
        await self.session.refresh(swap)
        
        return swap
    
    async def cancel(self, swap_id: int) -> Optional[ShiftSwap]:
        """Cancel swap request."""
        swap = await self.get_by_id(swap_id)
        if not swap:
            return None
        
        swap.status = SwapStatus.CANCELLED
        swap.updated_at = datetime.now()
        
        await self.session.commit()
        await self.session.refresh(swap)
        
        return swap
