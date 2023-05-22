from pydantic import BaseModel, Field


class AuthorGetOut(BaseModel):
    """AuthorGetOut is a class that defines the response model for get_author.
    """
    id: int = Field(title='Id of the book', ge=1)
    author_name: str = Field(title='Name of the author of the book', min_length=1, max_length=255)

    class Config:
        schema_extra = {
            'example': {
                'id': 1,
                'author_name': 'test author',
            }
        }


class AuthorGetAllOut(BaseModel):
    """AuthorGetAllOut is a class that defines the response model for get_all_authors.

    Parameters
    ----------
    books : list[BookGetOut]
        List of BookGetOut objects
    """

    authors: list[AuthorGetOut] = Field(..., title='authors')

    class Config:
        schema_extra = {
            'example': {
                'authors': [
                    {
                        'id': 1,
                        'author_name': 'test author',
                    },
                    {
                        'id': 2,
                        'author_name': 'test author2',
                    }
                ]
            }
        }
