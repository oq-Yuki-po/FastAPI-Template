from sqlalchemy.exc import IntegrityError

from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.repositories import UserRepository
from app.schemas import UserCreate


class DuplicateEmailError(Exception):
    """Raised when a registration conflicts with an existing email address."""


class AuthenticationError(Exception):
    """Raised when credentials or a token do not identify an active user."""


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def register(self, payload: UserCreate) -> User:
        email = str(payload.email).lower()
        if await self.repository.get_by_email(email) is not None:
            raise DuplicateEmailError
        user = User(email=email, hashed_password=hash_password(payload.password))
        self.repository.add(user)
        try:
            await self.repository.commit()
        except IntegrityError as error:
            # The unique constraint remains authoritative under concurrent requests.
            await self.repository.rollback()
            raise DuplicateEmailError from error
        await self.repository.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> str:
        user = await self.repository.get_by_email(email.lower())
        password_is_valid = verify_password(
            password, user.hashed_password if user is not None else DUMMY_PASSWORD_HASH
        )
        if user is None or not password_is_valid or not user.is_active:
            raise AuthenticationError
        return create_access_token(user.id)

    async def get_active_user(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError
        return user
