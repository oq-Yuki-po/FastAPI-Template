from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, String, select
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import relationship

from app import app_logger
from app.errors.exceptions import BookAlreadyExistsError
from app.models import AuthorModel, BaseModel, Engine, session


class BookModel(BaseModel):
    """
    BookModel
    """
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False, comment='book title')
    author_id = Column(Integer, ForeignKey(AuthorModel.id))
    isbn = Column(String(13), unique=True, nullable=False, comment='book isbn')
    cover_path = Column(String(256), unique=True, nullable=False, server_default="none", comment='book cover path')

    authors = relationship(AuthorModel, backref="books")

    def __init__(self,
                 title: str,
                 isbn: str,
                 cover_path: str,
                 author_id: Optional[int] = None,
                 authors: Optional[AuthorModel] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None) -> None:
        self.title = title
        self.isbn = isbn
        self.cover_path = cover_path
        self.author_id = author_id
        self.created_at = created_at
        self.updated_at = updated_at
        if authors is not None:
            self.authors = authors
        if author_id is not None:
            self.author_id = author_id

    def __repr__(self) -> str:
        return f"<BookModel(title={self.title}, isbn={self.isbn},"\
            f"cover_path={self.cover_path}, author_id={self.author_id})>"

    def save(self) -> None:
        """
        save book

        Returns
        -------
        book_id

        Raises
        ------
        BookAlreadyExistsError
        """

        if self.fetch_by_isbn(self.isbn) is None:
            session.add(self)
            session.flush()
            return self.id
        app_logger.error("Book title: %s isbn: %s already exists", self.title, self.isbn)
        raise BookAlreadyExistsError

    @classmethod
    def fetch_by_isbn(cls, isbn) -> Optional[BookModel]:
        """
        fetch book by isbn
        if book not exists, return None

        Returns
        -------
        Optional[BookModel|None]
        """

        fetch_result = session.scalars(select(cls).
                                       filter(cls.isbn == isbn)).\
            one_or_none()

        return fetch_result

    @classmethod
    def fetch_all(cls, offset: int, limit: int) -> list[Row]:
        """
        fetch all books

        Returns
        -------
        list[Row]
            BookModel.id, BookModel.title, BookModel.isbn, AuthorModel.name AS author_name
        """
        stmt = select(cls.id,
                      cls.title,
                      cls.isbn,
                      cls.cover_path,
                      AuthorModel.name.label("author_name")).join(cls.authors).\
            order_by(cls.id).\
            limit(limit).\
            offset(offset)
        """SQL Statement
            SELECT public.books.id,
                public.books.title,
                public.books.isbn,
                public.books.cover_path,
                public.authors.name AS author_name FROM public.books
                JOIN public.authors ON public.authors.id = public.books.author_id
            ORDER BY public.books.id
            LIMIT :param_1 OFFSET :param_2
        """
        fetch_result = session.execute(stmt).all()
        return fetch_result


if __name__ == "__main__":
    BaseModel.metadata.create_all(bind=Engine)
