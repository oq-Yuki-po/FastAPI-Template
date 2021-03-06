from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String

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

    def register(self) -> int:
        """登録処理

        Returns
        -------
        int
            著者ID
        """

        if (author := self.fetch_by_name(self.name)) is None:
            session.add(self)
            session.flush()
            return self.id
        else:
            return author.id

    @classmethod
    def fetch_by_name(cls, name: str) -> Optional[AuthorModel]:
        """著者名を条件に著者取得

        Parameters
        ----------
        name : str
            著者名

        Returns
        -------
        Optional[AuthorModel|None]
        """

        fetch_result = session.query(cls).\
            filter(cls.name == name).\
            one_or_none()

        return fetch_result

    @classmethod
    def fetch_all(cls) -> Optional[List[AuthorModel]]:
        """著者全権取得

        Returns
        -------
        Optional[List[AuthorModel]|None]
        """
        fetch_result = session.query(cls).\
            all()

        return fetch_result


if __name__ == "__main__":
    BaseModel.metadata.create_all(bind=Engine)
