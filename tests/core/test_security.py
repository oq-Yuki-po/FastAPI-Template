from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
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
    token = create_access_token(42)
    assert decode_access_token(token) == 42


def test_access_token_contains_required_security_claims() -> None:
    token = create_access_token(42)
    claims = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[ALGORITHM],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )
    assert claims["sub"] == "42"
    assert {"exp", "iat", "nbf", "iss", "aud", "jti"} <= claims.keys()


def test_expired_access_token_is_rejected() -> None:
    token = create_access_token(42, expires_delta=timedelta(seconds=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_token_for_another_audience_is_rejected() -> None:
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "42",
            "exp": now + timedelta(minutes=1),
            "iat": now,
            "nbf": now,
            "iss": settings.jwt_issuer,
            "aud": "another-service",
            "jti": "test-token",
        },
        settings.secret_key,
        algorithm=ALGORITHM,
    )
    with pytest.raises(jwt.InvalidAudienceError):
        decode_access_token(token)


def test_access_token_requires_numeric_subject() -> None:
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "not-a-user-id",
            "exp": now + timedelta(minutes=1),
            "iat": now,
            "nbf": now,
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "jti": "test-token",
        },
        settings.secret_key,
        algorithm=ALGORITHM,
    )
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)
