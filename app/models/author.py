from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, select

from app.models.setting import BaseModel, Engine, session


class AuthorModel(BaseModel):
    """
    AuthorModel
    """
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), unique=True, nullable=False, comment='author name')

    def __init__(self,
                 name: str,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None) -> None:

        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self) -> str:
        return f"<AuthorModel(name={self.name})>"

    def register(self) -> int:
        """
        register author

        Returns
        -------
        int
            registered author id
        """

        if (author := self.fetch_by_name(self.name)) is None:
            session.add(self)
            session.flush()
            return self.id
        return author.id

    @classmethod
    def fetch_by_name(cls, name: str) -> Optional[AuthorModel]:
        """
        fetch author by name

        Parameters
        ----------
        name : str
            author name

        Returns
        -------
        Optional[AuthorModel|None]
        """

        fetch_result = session.scalars(select(cls).
                                       where(cls.name == name)).\
            one_or_none()

        return fetch_result

    @classmethod
    def fetch_all(cls, offset: int, limit: int) -> Optional[list[AuthorModel]]:
        """
        fetch all authors

        Parameters
        ----------
        offset : int
            offset
        limit : int
            limit

        Returns
        -------
        Optional[List[AuthorModel]|None]
        """
        stmt = select(cls.id, cls.name).order_by(cls.id).limit(limit).offset(offset)
        """SQL Statement
            SELECT authors.id,
                authors.name
            FROM authors
            ORDER BY authors.id
            LIMIT :param_1 OFFSET :param_2
        """

        fetch_result = session.execute(stmt).all()

        return fetch_result


if __name__ == "__main__":
    BaseModel.metadata.create_all(bind=Engine)
