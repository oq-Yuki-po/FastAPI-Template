from pydantic import BaseModel, Field


class BookSaveIn(BaseModel):

    title: str = Field(..., title='title')
    isbn: str = Field(..., title='isbn')
    cover_path: str = Field(..., title='cover_path')
    author_name: str = Field(..., title='author_name')

    class Config:
        schema_extra = {
            'example': {
                'title': 'test book',
                'isbn': '9784774142232',
                'cover_path': 'test/path',
                'author_name': 'test author'
            }
        }
