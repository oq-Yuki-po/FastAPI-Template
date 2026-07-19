from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import UserRepository


async def test_user_repository_finds_user_by_email_and_id(db_session: AsyncSession) -> None:
    repository = UserRepository(db_session)
    user = User(email="repository@example.com", hashed_password="hash")
    repository.add(user)
    await repository.commit()
    await repository.refresh(user)

    assert await repository.get_by_email(user.email) is user
    assert await repository.get_by_id(user.id) is user


async def test_user_repository_returns_none_and_rolls_back(db_session: AsyncSession) -> None:
    repository = UserRepository(db_session)
    repository.add(User(email="rollback@example.com", hashed_password="hash"))

    await repository.rollback()

    assert await repository.get_by_email("rollback@example.com") is None
    assert await repository.get_by_id(999) is None
