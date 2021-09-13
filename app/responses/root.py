from pydantic import BaseModel, Field


class RootOut(BaseModel):

    message: str = Field(..., title='message')

    class Config:
        schema_extra = {
            'example': {
                'message': 'Hello World'
            }
        }
