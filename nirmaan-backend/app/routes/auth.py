from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.admin import Admin

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(data: LoginRequest):
    db: Session = SessionLocal()

    admin = db.query(Admin).filter(Admin.email == data.email).first()

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if admin.password_hash != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful"}