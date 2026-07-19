from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()
# Verify against a real Argon2 hash even when the account does not exist. This narrows
# the timing difference that could otherwise be used to enumerate registered emails.
DUMMY_PASSWORD_HASH = password_hash.hash("not-a-real-user-password")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(subject: int, expires_delta: timedelta | None = None) -> str:
    issued_at = datetime.now(UTC)
    expires_at = issued_at + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    claims = {
        "sub": str(subject),
        "exp": expires_at,
        "iat": issued_at,
        "nbf": issued_at,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "jti": str(uuid4()),
    }
    return jwt.encode(claims, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    # The algorithm is an application allowlist, never a value selected from the
    # untrusted JWT header. Issuer and audience prevent cross-service token reuse.
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[ALGORITHM],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        options={"require": ["sub", "exp", "iat", "nbf", "iss", "aud", "jti"]},
    )
    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise jwt.InvalidTokenError("Token subject must be a user ID")
    try:
        user_id = int(subject)
    except ValueError as error:
        raise jwt.InvalidTokenError("Token subject must be a user ID") from error
    # Database identifiers are positive. Rejecting zero/negative values avoids
    # carrying malformed identity data into repository queries and audit logs.
    if user_id <= 0:
        raise jwt.InvalidTokenError("Token subject must be a positive user ID")
    return user_id
