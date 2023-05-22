from pydantic import BaseModel, Field


class BookSaveOut(BaseModel):

    message: str = Field(title='message', min_length=1, max_length=255)

    class Config:
        schema_extra = {
            'example': {
                'message': 'success'
            }
        }


class BookGetOut(BaseModel):
    """BookGetOut is a class that defines the response model for get_book.
    """

    id: int = Field(title='Id of the book', ge=1)
    title: str = Field(title='Title of the book', min_length=1, max_length=255)
    isbn: str = Field(title='ISBN code of the book', min_length=13, max_length=13)
    author_name: str = Field(title='Name of the author of the book', min_length=1, max_length=255)
    published_at: str = Field(title='Date of publication of the book')
    cover_base64_image: str = Field(title='Base64 encoded image of the cover of the book')

    class Config:
        schema_extra = {
            'example': {
                'id': 1,
                'title': 'test book',
                'isbn': '9784774142232',
                'author_name': 'test author',
                'published_at': '2020-01-01',
                'cover_base64_image': 'iVBORw0KGgoAAAANSUhEUgAAASwAAAEsAQAAAABRBrPYAAABpElEQVR4nO3BMQEAAADCoPV'
            }
        }


class BookGetAllOut(BaseModel):
    """BookGetAllOut is a class that defines the response model for get_all_books.

    Parameters
    ----------
    books : list[BookGetOut]
        List of BookGetOut objects
    """

    books: list[BookGetOut] = Field(..., title='books')

    class Config:
        schema_extra = {
            'example': {
                'books': [
                    {
                        'id': 1,
                        'title': 'test book',
                        'isbn': '9784774142232',
                        'author_name': 'test author',
                        'published_at': '2020-01-01',
                        'cover_base64_image': 'iVBORw0KGgoAAAANSUhEUgAAASwAAAEsAQAAAABRBrPYAAABpElEQVR4nO3BMQEAAADCoPV'
                    },
                    {
                        'id': 2,
                        'title': 'test book2',
                        'isbn': '9784774142233',
                        'author_name': 'test author2',
                        'published_at': '2020-01-02',
                        'cover_base64_image': 'iVBORw0KGgoAAAANSUhEUgAAASwAAAEsAQAAAABRBrPYAAABpElEQVR4nO3BMQEAAADCoPV'
                    }
                ]
            }
        }
