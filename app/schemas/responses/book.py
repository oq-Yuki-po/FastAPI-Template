from pydantic import BaseModel, Field


class BookSaveOut(BaseModel):

    message: str = Field(..., title='message')

    class Config:
        schema_extra = {
            'example': {
                'message': 'success'
            }
        }
