from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from starlette import status

router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class CreateUserRequest(BaseModel):
  name: str
  email: str
  createAt: None
  photoUrl: str
  password: str
  role: str


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
  create_user_model = Users(
    name=create_user_request.name,
    email=create_user_request.email,
    createAt=create_user_request.createAt,
    photoUrl=create_user_request.photoUrl,
    hashed_password=bcrypt_context.hash(create_user_request.password),
    role=create_user_request.role,
    is_active=True
  )
  
  db.add(create_user_model)
  db.commit()
