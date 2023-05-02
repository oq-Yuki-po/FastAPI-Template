import yaml
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi_versioning import VersionedFastAPI

from app.middleware.exception_middleware import ExceptionMiddleware
from app.models.setting import initialize_db, initialize_table
from app.routers import book_router

APP_TITLE = "FastAPI Template"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "This is a smple FastAPI template"

app = FastAPI(title=APP_TITLE,
              version=APP_VERSION,
              description=APP_DESCRIPTION)

app.include_router(book_router)
app.add_middleware(ExceptionMiddleware)

app = VersionedFastAPI(app,
                       version_format='{major}.{minor}',
                       prefix_format='/v{major}.{minor}',
                       enable_latest=True)


@app.on_event("startup")
async def startup_event():
    initialize_db()
    initialize_table()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=APP_TITLE,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def export_swagger():

    with open("openapi.yaml", "w", encoding="utf-8") as file:
        file.write(yaml.dump(custom_openapi()))


if __name__ == "__main__":
    export_swagger()
