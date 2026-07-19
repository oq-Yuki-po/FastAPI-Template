from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class UserRepository:
    """Provides the persistence operations used by authentication services."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        users = await self.session.scalars(select(User).where(User.id == user_id))
        return users.first()

    async def get_by_email(self, email: str) -> User | None:
        users = await self.session.scalars(select(User).where(User.email == email))
        return users.first()

    def add(self, user: User) -> None:
        self.session.add(user)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def refresh(self, user: User) -> None:
        await self.session.refresh(user)
