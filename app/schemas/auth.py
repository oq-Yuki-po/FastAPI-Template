from pydantic import EmailStr, Field

from app.schemas.common import ApiModel


class UserCreate(ApiModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class UserRead(ApiModel):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool


class Token(ApiModel):
    access_token: str
    token_type: str = "bearer"
