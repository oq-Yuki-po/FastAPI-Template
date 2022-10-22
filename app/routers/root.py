from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

class RootIn(BaseModel):

    message: str = Field(..., title='message')

    class Config:
        schema_extra = {
            'example': {
                'message': 'Hello World'
            }
        }
