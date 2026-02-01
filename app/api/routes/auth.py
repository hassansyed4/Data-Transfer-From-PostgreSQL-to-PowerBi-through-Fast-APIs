from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT id, tenant_id, role, password_hash, is_active FROM users WHERE email=:email"),
        {"email": payload.email},
    ).mappings().first()

    if not row or not row["is_active"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(sub=str(row["id"]), tenant_id=str(row["tenant_id"]), role=row["role"])
    return {"access_token": token, "token_type": "bearer"}
