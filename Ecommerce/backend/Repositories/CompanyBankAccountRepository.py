from Models.CompanyBankAccount import CompanyBankAccount
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class CompanyBankAccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = CompanyBankAccount

    async def get_main_account(self) -> CompanyBankAccount:
        result = await self.db.execute(select(CompanyBankAccount).limit(1))
        return result.scalar_one_or_none()
