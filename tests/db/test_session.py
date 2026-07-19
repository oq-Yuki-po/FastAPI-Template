from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_database_session_executes_query(db_session: AsyncSession) -> None:
    assert await db_session.scalar(text("SELECT 1")) == 1
