from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String

from app.models.setting import BaseModel, Engine


class AuthorModel(BaseModel):
    """
    AuthorModel
    """
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256))

    def __init__(self,
                 name: str,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None) -> None:

        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at


if __name__ == "__main__":
    BaseModel.metadata.create_all(bind=Engine)
