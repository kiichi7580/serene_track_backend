from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from contextlib import contextmanager

router = APIRouter(
  prefix='/auth',
  tags=['auth']
)

SECRET_KEY = 'c4644434a0567efcc411a4b377d2f9c2df6c066eca06f7791eea9e4cdbe18562'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
  name: str
  email: str
  photo_url: str
  short_term_goal: str
  long_term_goal: str
  password: str
  role: str


class Token(BaseModel):
  access_token: str
  token_type: str


@contextmanager
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
  user = db.query(Users).filter(Users.name == username).first()
  if not user:
    return False
  if not bcrypt_context.verify(password, user.hashed_password):
    return False
  return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):

  encode = {'sub': username, 'id': user_id, 'role': role}
  expires = datetime.now(timezone.utc) + expires_delta
  encode.update({'exp': expires})
  return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get('sub')
    user_id: str = payload.get('id')
    user_role: str = payload.get('role')
    if username is None or user_id is None:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Could not validate user.')
    return {'username': username, 'id': user_id, 'user_role': user_role}
  except JWTError: 
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Could not validate user.')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
  create_user_model = Users(
    name=create_user_request.name,
    email=create_user_request.email,
    created_at=datetime.now(timezone.utc),
    photo_url=create_user_request.photo_url,
    short_term_goal=create_user_request.short_term_goal,
    long_term_goal=create_user_request.long_term_goal,
    hashed_password=bcrypt_context.hash(create_user_request.password),
    role=create_user_request.role,
    is_active=True,
    health_data_integration_status=False,
  )
  
  db.add(create_user_model)
  db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                  db: db_dependency):
  user = authenticate_user(form_data.username, form_data.password, db)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Could not validate user.')
  token = create_access_token(user.name, user.id, user.role, timedelta(minutes=30))

  return {'access_token': token, 'token_type': 'bearer'}