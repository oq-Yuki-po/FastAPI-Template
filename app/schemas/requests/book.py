from pydantic import BaseModel, Field


class BookSaveIn(BaseModel):

    title: str = Field(title='title', min_length=1, max_length=255)
    isbn: str = Field(title='isbn', min_length=13, max_length=13)
    cover_path: str = Field(title='cover_path', min_length=1, max_length=255)
    author_name: str = Field(title='author_name', min_length=1, max_length=255)

    class Config:
        schema_extra = {
            'example': {
                'title': 'test book',
                'isbn': '9784774142232',
                'cover_path': 'test/path',
                'author_name': 'test author'
            }
        }
