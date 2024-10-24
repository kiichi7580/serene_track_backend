from typing import Annotated, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Form
from models import Todos
from starlette import status
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime, timezone

router = APIRouter()


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
  title: str = Field(min_length=3)
  description: str = Field(min_length=3, max_length=100)
  complete: bool
  category_id: str
  created_at: datetime
  notification_time: Optional[datetime] = None


@router.get("/todo/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication Failed')
  
  return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication Failed')
  
  todo_model = db.query(Todos).filter(Todos.id == todo_id)\
    .filter(Todos.owner_id == user.get('id')).first()
  if todo_model is not None:
    return todo_model
  raise HTTPException(status_code=404, detail='Todo not found.')


@router.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency,
                      title: str = Form(...), description: str = Form(...), complete: bool = Form(...),
                      category_id: str = Form(...), notification_time: Optional[datetime] = Form(None)):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication Failed')

  todo_request = TodoRequest(
    title=title,
    description=description,
    complete=complete,
    category_id=category_id,
    created_at=datetime.now(timezone.utc),
    notification_time=notification_time,
  )

  todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

  db.add(todo_model)
  db.commit()
  db.refresh(todo_model)

  return todo_model


@router.put("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0),
                      title: str = Form(...), description: str = Form(...), complete: bool = Form(...),
                      category_id: str = Form(...), notification_time: Optional[datetime] = Form(None)):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication Failed')

  todo_model = db.query(Todos).filter(Todos.id == todo_id)\
    .filter(Todos.owner_id == user.get('id')).first()
  if todo_model is None:
    raise HTTPException(status_code=404, detail='Todo not found.')
  
  todo_model.title = title
  todo_model.description = description
  todo_model.complete = complete
  todo_model.category_id = category_id
  todo_model.notification_time = notification_time

  db.add(todo_model)
  db.commit()
  db.refresh(todo_model)

  return todo_model

@router.put("/todo/complete/{todo_id}", status_code=status.HTTP_200_OK)
async def change_complete_status(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0), complete: bool = Form(...)):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication Failed')

  todo_model = db.query(Todos).filter(Todos.id == todo_id)\
    .filter(Todos.owner_id == user.get('id')).first()
  if todo_model is None:
    raise HTTPException(status_code=404, detail='Todo not found.')

  todo_model.complete = complete

  db.add(todo_model)
  db.commit()
  db.refresh(todo_model)

  return todo_model

@router.put("/todo/notification_time/{todo_id}", status_code=status.HTTP_200_OK)
async def off_todo_notification(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0), notification_time: Optional[datetime] = Form(None)):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication Failed')

  todo_model = db.query(Todos).filter(Todos.id == todo_id)\
    .filter(Todos.owner_id == user.get('id')).first()
  if todo_model is None:
    raise HTTPException(status_code=404, detail='Todo not found.')

  todo_model.notification_time = notification_time

  db.add(todo_model)
  db.commit()
  db.refresh(todo_model)

  return todo_model

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication Failed')

  todo_model = db.query(Todos).filter(Todos.id == todo_id)\
    .filter(Todos.owner_id == user.get('id')).first()
  if todo_model is None:
    raise HTTPException(status_code=404, detail='Todo not found')
  
  db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
  db.commit()