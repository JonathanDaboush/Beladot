from sqlalchemy.ext.asyncio import AsyncSession
from Models.Wishlist import Wishlist


class WishlistRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Wishlist
