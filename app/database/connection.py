from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import sessionLocal


async def get_db():
    """Get a database session."""
    async with sessionLocal() as session:
        yield session
