from datetime import date
from typing import Any

import factory

from app.schemas import AuthorRead, BookCreate, BookRead, UserCreate, UserRead


class AuthorReadFactory(factory.Factory[AuthorRead]):
    class Meta:
        model = AuthorRead

    id = factory.Sequence(lambda number: number + 1)
    name = factory.Sequence(lambda number: f"Author {number}")


class BookCreateFactory(factory.Factory[BookCreate]):
    class Meta:
        model = BookCreate

    title = factory.Sequence(lambda number: f"Book {number}")
    isbn = factory.Sequence(lambda number: f"{number:013d}")
    author_name = factory.Sequence(lambda number: f"Author {number}")
    cover_url: Any = factory.Faker("url")
    published_at = factory.LazyFunction(date.today)


class BookReadFactory(factory.Factory[BookRead]):
    class Meta:
        model = BookRead

    id = factory.Sequence(lambda number: number + 1)
    title = factory.Sequence(lambda number: f"Book {number}")
    isbn = factory.Sequence(lambda number: f"{number:013d}")
    cover_url: Any = factory.Faker("url")
    published_at = factory.LazyFunction(date.today)
    author: Any = factory.SubFactory(AuthorReadFactory)


class UserCreateFactory(factory.Factory[UserCreate]):
    class Meta:
        model = UserCreate

    email = factory.Sequence(lambda number: f"user{number}@example.com")
    password: Any = factory.Faker("password", length=16)


class UserReadFactory(factory.Factory[UserRead]):
    class Meta:
        model = UserRead

    id = factory.Sequence(lambda number: number + 1)
    email = factory.Sequence(lambda number: f"user{number}@example.com")
    is_active = True
    is_superuser = False
