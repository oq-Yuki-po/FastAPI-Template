from datetime import date
from typing import Any

import factory

from app.models import Author, Book, User


class AuthorFactory(factory.Factory[Author]):
    class Meta:
        model = Author

    name = factory.Sequence(lambda number: f"Author {number}")


class BookFactory(factory.Factory[Book]):
    class Meta:
        model = Book

    title = factory.Sequence(lambda number: f"Book {number}")
    isbn = factory.Sequence(lambda number: f"{number:013d}")
    cover_url: Any = factory.Faker("url")
    published_at = factory.LazyFunction(date.today)
    author: Any = factory.SubFactory(AuthorFactory)


class UserFactory(factory.Factory[User]):
    class Meta:
        model = User

    email = factory.Sequence(lambda number: f"user{number}@example.com")
    hashed_password: Any = factory.Faker("sha256")
    is_active = True
    is_superuser = False
