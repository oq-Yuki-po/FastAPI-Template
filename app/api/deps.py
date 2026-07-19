from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import User
from app.repositories import CatalogRepository, UserRepository
from app.services import AuthenticationError, AuthService, CatalogService

DbSession = Annotated[AsyncSession, Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/token")


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(UserRepository(db))


def get_catalog_service(db: DbSession) -> CatalogService:
    return CatalogService(CatalogRepository(db))


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CatalogServiceDep = Annotated[CatalogService, Depends(get_catalog_service)]


async def get_current_user(
    service: AuthServiceDep, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_access_token(token)
    except jwt.InvalidTokenError as error:
        raise credentials_error from error
    try:
        return await service.get_active_user(user_id)
    except AuthenticationError as error:
        raise credentials_error from error


CurrentUser = Annotated[User, Depends(get_current_user)]
