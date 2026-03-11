from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.utils.jwt_handler import decode_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_payload(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    try:
        return decode_token(creds.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def require_role(required: str):
    def _dep(payload: dict = Depends(get_current_user_payload)) -> dict:
        role = payload.get("role")
        if role != required:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return payload

    return _dep


require_admin = require_role("admin")
require_doctor = require_role("doctor")
