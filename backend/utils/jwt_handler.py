from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

from backend.core.config import settings

def create_access_token(*, subject: str, role: str) -> str:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is not set. Create a .env based on env.example.")

    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": exp,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

