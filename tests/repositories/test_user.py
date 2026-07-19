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
