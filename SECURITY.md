# Security

## Implemented controls

- Passwords are hashed with pwdlib's recommended Argon2 configuration.
- Login performs an Argon2 verification for missing accounts to reduce timing-based email enumeration.
- JWT verification uses a fixed algorithm allowlist and requires `sub`, `exp`, `iat`, `nbf`, `iss`, `aud`, and `jti` claims.
- JWT subjects use immutable user IDs rather than mutable email addresses.
- Inactive users cannot obtain or use access tokens.
- Staging and production reject the repository's documented development secret.
- Staging and production reject placeholder-style secrets such as `replace-*` and `change-me-*`.
- Credentialed CORS rejects wildcard origins.
- Trusted-host validation rejects forged `Host` headers; production forbids wildcard hosts.
- Browser defense headers prevent MIME sniffing, framing, referrer leakage, and sensitive-device APIs.
- Staging and production disable Swagger, ReDoc, and the OpenAPI endpoint and add CSP and HSTS.
- Token responses use `Cache-Control: no-store` and `Pragma: no-cache`.
- JWT user identifiers must be positive database IDs.
- Database uniqueness constraints remain authoritative during concurrent registration.
- CI runs Bandit and audits locked production dependencies with pip-audit.

## Deployment responsibilities

This repository is an application template, so the deployment platform must still provide:

- HTTPS at every externally reachable endpoint.
- Correct `ALLOWED_HOSTS` and `CORS_ORIGINS` values for every public hostname and frontend origin.
- A randomly generated `SECRET_KEY` stored in a secret manager and a rotation procedure.
- Rate limiting for registration and token endpoints at the gateway or application layer.
- Centralized security logs and alerts without logging passwords or bearer tokens.
- Database encryption, least-privilege credentials, backups, and network restrictions.
- A token revocation strategy if immediate logout or incident response is required. Current access
  tokens are stateless and remain valid until their short expiration time.

HSTS is emitted in staging and production. Only expose those environments through HTTPS; serving
them over plain HTTP would cause clients that previously received HSTS to refuse the connection.

## Reporting a vulnerability

Do not open a public issue containing exploit details or credentials. Contact the repository owner
privately with affected versions, reproduction steps, and expected impact.
