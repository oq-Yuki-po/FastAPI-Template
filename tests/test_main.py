from app.main import app


def test_openapi_contains_versioned_routes() -> None:
    paths = app.openapi()["paths"]
    assert "/api/v1/auth/token" in paths
    assert "/api/v1/books" in paths
