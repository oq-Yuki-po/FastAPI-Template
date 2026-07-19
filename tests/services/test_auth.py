from unittest.mock import AsyncMock, Mock

import pytest

from app.core.security import hash_password
from app.models import User
from app.schemas import UserCreate
from app.services import AuthenticationError, AuthService, DuplicateEmailError


async def test_register_rejects_existing_email() -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(return_value=User())
    service = AuthService(repository)

    with pytest.raises(DuplicateEmailError):
        await service.register(
            UserCreate(email="existing@example.com", password="a-secure-password")
        )


async def test_authenticate_returns_token_for_active_user() -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(
        return_value=User(
            id=7,
            email="active@example.com",
            hashed_password=hash_password("a-secure-password"),
            is_active=True,
        )
    )
    service = AuthService(repository)

    token = await service.authenticate("ACTIVE@example.com", "a-secure-password")

    assert isinstance(token, str)
    repository.get_by_email.assert_awaited_once_with("active@example.com")


async def test_authenticate_rejects_inactive_user() -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(
        return_value=User(
            id=7,
            email="inactive@example.com",
            hashed_password=hash_password("a-secure-password"),
            is_active=False,
        )
    )

    with pytest.raises(AuthenticationError):
        await AuthService(repository).authenticate("inactive@example.com", "a-secure-password")
