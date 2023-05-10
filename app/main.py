import yaml
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi_versioning import VersionedFastAPI

from app.middleware.exception_middleware import ExceptionMiddleware
from app.models.setting import initialize_db, initialize_table
from app.routers import book_router

APP_TITLE = "FastAPI Template"
APP_VERSION = "1.0"
APP_DESCRIPTION = "This is a smple FastAPI template"

app = FastAPI(title=APP_TITLE,
              version=APP_VERSION,
              description=APP_DESCRIPTION)

app.include_router(book_router)
app.add_middleware(ExceptionMiddleware)

app = VersionedFastAPI(app,
                       version_format='{major}.{minor}',
                       prefix_format='/v{major}.{minor}',
                       enable_latest=False)


@app.on_event("startup")
async def startup_event():
    initialize_db()
    initialize_table()


def custom_openapi(api_version):
    if app.openapi_schema:
        return app.openapi_schema
    for i in app.router.routes:
        if i.path == f"/v{api_version}":
            tarrget_router = i
    openapi_schema = get_openapi(
        title=APP_TITLE,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        routes=tarrget_router.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def export_swagger():
    api_versions = ["1.0"]

    for api_version in api_versions:
        with open(f"openapi_{api_version}.yaml", "w", encoding="utf-8") as file:
            file.write(yaml.dump(custom_openapi(api_version)))


if __name__ == "__main__":
    export_swagger()
