import unittest

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import engine

class DatabaseTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.connection = await engine.connect()
        self.transaction = await self.connection.begin()
        self.session = AsyncSession(
            bind=self.connection,
            join_transaction_mode='create_savepoint',
            expire_on_commit=False
        )
    
    async def asyncTearDown(self):
        await self.session.close()
        await self.transaction.rollback()
        await self.connection.close()
        await engine.dispose()

