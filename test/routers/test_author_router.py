from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.factories import AuthorFactory
from app.routers.setting import AppRoutes
from app.schemas.responses import AuthorGetAllOut, AuthorGetOut

TEST_URL = f"{AppRoutes.API_VERSION}{AppRoutes.Authors.PREFIX}"


def test_get_authors(app_client: TestClient, db_session: Session) -> None:
    """
    Test get_authors
    """
    author1 = AuthorFactory(name="test author1")
    author2 = AuthorFactory(name="test author2")
    author3 = AuthorFactory(name="test author3")

    db_session.add_all([author1, author2, author3])
    db_session.commit()

    response = app_client.get(f"{TEST_URL}{AppRoutes.Authors.GET_URL}?offset=0&limit=10")

    expected_result = AuthorGetAllOut(authors=[AuthorGetOut(id=i.id,
                                                            author_name=i.name,
                                                            ) for i in [author1, author2, author3]])
    assert response.status_code == 200
    assert response.json() == expected_result.dict()
