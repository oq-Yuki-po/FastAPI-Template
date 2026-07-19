from collections.abc import AsyncGenerator
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import session as session_module


async def test_database_session_executes_query(db_session: AsyncSession) -> None:
    assert await db_session.scalar(text("SELECT 1")) == 1


async def test_get_db_rolls_back_when_request_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Mock(spec=AsyncSession)
    session.rollback = AsyncMock()
    context = AsyncMock()
    context.__aenter__.return_value = session
    monkeypatch.setattr(session_module, "SessionFactory", Mock(return_value=context))
    dependency = cast(AsyncGenerator[AsyncSession, None], session_module.get_db())

    assert await anext(dependency) is session
    with pytest.raises(RuntimeError, match="request failed"):
        await dependency.athrow(RuntimeError("request failed"))

    session.rollback.assert_awaited_once()
