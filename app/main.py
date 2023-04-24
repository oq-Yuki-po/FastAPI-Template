from fastapi import FastAPI

from app.middleware.exception_middleware import ExceptionMiddleware
from app.models.setting import initialize_db, initialize_table
from app.routers import book_router

app = FastAPI(title="FastAPI Template", version="1.0.0")


app.include_router(book_router)
app.add_middleware(ExceptionMiddleware)


@app.on_event("startup")
async def startup_event():
    initialize_db()
    initialize_table()
