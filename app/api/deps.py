from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.core.security import decode_token

bearer = HTTPBearer()

def get_current_claims(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    try:
        return decode_token(creds.credentials)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def require_role(allowed: set[str]):
    def _inner(claims: dict = Depends(get_current_claims)) -> dict:
        if claims.get("role") not in allowed:
            raise HTTPException(status_code=403, detail="Not authorized")
        return claims
    return _inner
