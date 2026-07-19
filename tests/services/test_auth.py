from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.schemas import UserCreate
from app.services import AuthenticationError, AuthService, DuplicateEmailError
from tests.factories import UserFactory


async def test_register_rejects_existing_email() -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(return_value=UserFactory.build())
    service = AuthService(repository)

    with pytest.raises(DuplicateEmailError):
        await service.register(
            UserCreate(email="existing@example.com", password="a-secure-password")
        )


async def test_register_persists_normalized_email() -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(return_value=None)
    repository.commit = AsyncMock()
    repository.refresh = AsyncMock()
    service = AuthService(repository)

    user = await service.register(
        UserCreate(email="Developer@EXAMPLE.COM", password="a-secure-password")
    )

    assert user.email == "developer@example.com"
    repository.add.assert_called_once_with(user)
    repository.commit.assert_awaited_once()
    repository.refresh.assert_awaited_once_with(user)


async def test_register_rolls_back_integrity_conflict() -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(return_value=None)
    repository.commit = AsyncMock(
        side_effect=IntegrityError("INSERT users", {}, RuntimeError("duplicate"))
    )
    repository.rollback = AsyncMock()

    with pytest.raises(DuplicateEmailError):
        await AuthService(repository).register(
            UserCreate(email="race@example.com", password="a-secure-password")
        )

    repository.rollback.assert_awaited_once()
    repository.refresh.assert_not_called()


async def test_authenticate_returns_token_for_active_user() -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(
        return_value=UserFactory.build(
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
        return_value=UserFactory.build(
            id=7,
            email="inactive@example.com",
            hashed_password=hash_password("a-secure-password"),
            is_active=False,
        )
    )

    with pytest.raises(AuthenticationError):
        await AuthService(repository).authenticate("inactive@example.com", "a-secure-password")


async def test_authenticate_rejects_missing_user() -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(return_value=None)

    with pytest.raises(AuthenticationError):
        await AuthService(repository).authenticate("missing@example.com", "a-secure-password")


async def test_get_active_user_returns_active_user() -> None:
    user = UserFactory.build(id=7, is_active=True)
    repository = Mock()
    repository.get_by_id = AsyncMock(return_value=user)

    result = await AuthService(repository).get_active_user(7)

    assert result is user


@pytest.mark.parametrize("user", [None, UserFactory.build(is_active=False)])
async def test_get_active_user_rejects_missing_or_inactive_user(user: object) -> None:
    repository = Mock()
    repository.get_by_id = AsyncMock(return_value=user)

    with pytest.raises(AuthenticationError):
        await AuthService(repository).get_active_user(7)
