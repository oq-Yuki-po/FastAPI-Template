import ast

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


def test_main():

    client = TestClient(app)

    response = client.get("/")

    assert ast.literal_eval(response.text) == {"message": "Hello World"}
    assert response.status_code == status.HTTP_200_OK
