import yaml
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI Template",
        version="1.0.0",
        description="This is a smple OpenAPI schema",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def export_swagger():

    print(yaml.dump(custom_openapi()))

if __name__ == "__main__":
    export_swagger()
