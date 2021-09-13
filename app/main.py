from fastapi import FastAPI, status

from app.models.setting import initialize_db
from app.requests import RootIn
from app.responses import ErrorMessage, InvalidRequestErrorOut, Root500ErrorClass, RootOut

app = FastAPI(title="FastAPI Template", version="1.0.0")

initialize_db()


@app.get("/",
         tags=['root'],
         response_model=RootOut,
         responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {'description': f'{ErrorMessage.INTERNAL_SERVER_ERROR}'
                                                            f'<br>{ErrorMessage.DATABASE_CONNECTION_ERROR}'
                                                            f'<br>{ErrorMessage.DATABASE_ERROR}',
                                                            'model': Root500ErrorClass}
                    })
async def root(message: str) -> RootOut:
    return RootOut(message=message)


@app.post("/",
          tags=['root'],
          response_model=RootOut,
          responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {'description': f'{ErrorMessage.INTERNAL_SERVER_ERROR}'
                                                             f'<br>{ErrorMessage.DATABASE_CONNECTION_ERROR}'
                                                             f'<br>{ErrorMessage.DATABASE_ERROR}',
                                                             'model': Root500ErrorClass}
                     })
async def root(rout_in: RootIn) -> RootOut:
    return RootOut(message=rout_in.message)
