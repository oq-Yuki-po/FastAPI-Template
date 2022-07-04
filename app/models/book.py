from datetime import datetime
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models import AuthorModel
from app.models.setting import BaseModel, Engine


class BookModel(BaseModel):
    """
    BookModel
    """
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256))
    author_id = Column(Integer, ForeignKey(AuthorModel.id))
    isbn = Column(String(13))
    cover_path = Column(String(256))

    authors = relationship(AuthorModel, backref="books")

    def __init__(self,
                 title: str,
                 isbn: str,
                 cover_path: str,
                 author_id: str,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None) -> None:
        self.title = title
        self.isbn = isbn
        self.cover_path = cover_path
        self.author_id = author_id
        self.created_at = created_at
        self.updated_at = updated_at


if __name__ == "__main__":
    BaseModel.metadata.create_all(bind=Engine)
