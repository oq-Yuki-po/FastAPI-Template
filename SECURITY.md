# Security

## Implemented controls

- Passwords are hashed with pwdlib's recommended Argon2 configuration.
- Login performs an Argon2 verification for missing accounts to reduce timing-based email enumeration.
- JWT verification uses a fixed algorithm allowlist and requires `sub`, `exp`, `iat`, `nbf`, `iss`, `aud`, and `jti` claims.
- JWT subjects use immutable user IDs rather than mutable email addresses.
- Inactive users cannot obtain or use access tokens.
- Staging and production reject the repository's documented development secret.
- Credentialed CORS rejects wildcard origins.
- Database uniqueness constraints remain authoritative during concurrent registration.
- CI runs Bandit and audits locked production dependencies with pip-audit.

## Deployment responsibilities

This repository is an application template, so the deployment platform must still provide:

- HTTPS at every externally reachable endpoint.
- A randomly generated `SECRET_KEY` stored in a secret manager and a rotation procedure.
- Rate limiting for registration and token endpoints at the gateway or application layer.
- Centralized security logs and alerts without logging passwords or bearer tokens.
- Database encryption, least-privilege credentials, backups, and network restrictions.
- A token revocation strategy if immediate logout or incident response is required. Current access
  tokens are stateless and remain valid until their short expiration time.

## Reporting a vulnerability

Do not open a public issue containing exploit details or credentials. Contact the repository owner
privately with affected versions, reproduction steps, and expected impact.
