import json
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models import Users
from starlette import status
from database import SessionLocal
from .auth import get_current_user, CreateUserRequest, authenticate_user, create_access_token, Token
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta

router = APIRouter(
  prefix='/user',
  tags=['user'],
)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class ChangeEmail(BaseModel):
    email: str
    new_email: str = Field(min_length=6)

class ChangePassword(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class InputUserInformation(BaseModel):
    email: str
    password: str


class updateUserInformation(BaseModel):
    name: str
    photo_url: str
    short_term_goal: str
    long_term_goal: str
    health_data_integration_status: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user_model


@router.post("/sign_up",  response_model=Token)
async def sign_up(db: db_dependency, input_user_information: InputUserInformation):
    user_model = db.query(Users).filter(Users.email == input_user_information.email).first()
    if user_model is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    create_user_model = Users(
        name='',
        email=input_user_information.email,
        created_at=datetime.now(timezone.utc),
        photo_url='',
        short_term_goal='',
        long_term_goal='',
        hashed_password=bcrypt_context.hash(input_user_information.password),
        role='user',
        is_active=True,
        health_data_integration_status=False,
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    user = db.query(Users).filter(Users.email == input_user_information.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    token = create_access_token(user.name, user.id, user.role, timedelta(minutes=30))

    return {'access_token': token, 'token_type': 'Bearer'}


@router.post("/sign_in", response_model=Token)
async def sign_in(db: db_dependency, input_user_information: InputUserInformation):
    user = db.query(Users).filter(Users.email == input_user_information.email).first()
    if not user or not bcrypt_context.verify(input_user_information.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    token = create_access_token(user.name, user.id, user.role, timedelta(minutes=30))

    return {'access_token': token, 'token_type': 'Bearer'}


@router.put("/email", status_code=status.HTTP_204_NO_CONTENT)
async def change_email(user: user_dependency, db: db_dependency, change_email: ChangeEmail):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_model.email != change_email.email:
        raise HTTPException(status_code=401, detail='Error on email change')

    user_model.email = change_email.new_email
    db.add(user_model)
    db.commit()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, change_password: ChangePassword):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not bcrypt_context.verify(change_password.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(change_password.new_password)
    db.add(user_model)
    db.commit()


@router.put("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(db: db_dependency, update_user_information: updateUserInformation, user_id: int = Path(gt=0)):
    # if user is None:
    #     raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model.name = update_user_information.name
    user_model.photo_url = update_user_information.photo_url
    user_model.short_term_goal = update_user_information.short_term_goal
    user_model.long_term_goal = update_user_information.long_term_goal
    user_model.health_data_integration_status = update_user_information.health_data_integration_status

    db.add(user_model)
    db.commit()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()