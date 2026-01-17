





from backend.persistance.refund_request import RefundRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class RefundRequestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, refund_request_id):
        result = await self.db.execute(
            select(RefundRequest).filter(RefundRequest.refund_request_id == refund_request_id)
        )
        return result.scalars().first()

    async def save(self, refund_request):
        """
        Save a RefundRequest instance, including the description field if present.
        """
        self.db.add(refund_request)
        await self.db.commit()
        await self.db.refresh(refund_request)
        return refund_request

    async def update(self, refund_request_id, **kwargs):
        """
        Update a RefundRequest instance by id, including the description field if provided in kwargs.
        """
        refund_request = await self.get_by_id(refund_request_id)
        if not refund_request:
            return None
        for k, v in kwargs.items():
            if hasattr(refund_request, k):
                setattr(refund_request, k, v)
        await self.db.commit()
        return refund_request

    async def delete(self, refund_request_id):
        refund_request = await self.get_by_id(refund_request_id)
        if refund_request:
            await self.db.delete(refund_request)
            await self.db.commit()
            return True
        return False
