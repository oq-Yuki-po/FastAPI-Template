from datetime import date

from pydantic import Field

from app.schemas.common import ApiModel, Page


class AuthorRead(ApiModel):
    id: int
    name: str


class AuthorPage(Page):
    items: list[AuthorRead]


class BookCreate(ApiModel):
    title: str = Field(min_length=1, max_length=255)
    isbn: str = Field(pattern=r"^\d{13}$")
    author_name: str = Field(min_length=1, max_length=255)
    cover_url: str | None = Field(default=None, max_length=2048)
    published_at: date


class BookRead(ApiModel):
    id: int
    title: str
    isbn: str
    cover_url: str | None
    published_at: date
    author: AuthorRead


class BookPage(Page):
    items: list[BookRead]
