from sqlalchemy.ext.asyncio import AsyncSession
from Models.WishlistItem import WishlistItem


class WishlistItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = WishlistItem
