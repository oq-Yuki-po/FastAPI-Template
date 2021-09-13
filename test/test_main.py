import ast

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


def test_root_get(app_client):

    message = "Testing"
    response = app_client.get("/", params={"message": message})

    assert ast.literal_eval(response.text) == {"message": message}
    assert response.status_code == status.HTTP_200_OK

def test_root_post(app_client):

    message = "Testing"
    response = app_client.post("/", json={"message": message})

    assert ast.literal_eval(response.text) == {"message": message}
    assert response.status_code == status.HTTP_200_OK
