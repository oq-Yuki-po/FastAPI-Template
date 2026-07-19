import jwt

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_round_trip() -> None:
    password = "a-secure-password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_round_trip() -> None:
    token = create_access_token("dev@example.com")
    assert decode_access_token(token) == "dev@example.com"


def test_access_token_requires_subject() -> None:
    from app.core.config import settings
    from app.core.security import ALGORITHM

    token = jwt.encode({}, settings.secret_key, algorithm=ALGORITHM)
    try:
        decode_access_token(token)
    except jwt.InvalidTokenError:
        pass
    else:
        raise AssertionError("Token without a subject must be rejected")
