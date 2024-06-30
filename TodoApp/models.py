from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func


class Users(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, unique=True)
  email = Column(String, unique=True)
  createAt = Column(DateTime, default=func.now())
  photoUrl = Column(String)
  hashed_password = Column(String)
  is_active = Column(Boolean, default=True)
  role = Column(String)


class Todos(Base):
  __tablename__ = 'todos'

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String)
  description = Column(String)
  complete = Column(Boolean, default=False)
  category_id = Column(String)
  date = Column(DateTime, default=func.now())
  owner_id = Column(Integer, ForeignKey("users.id"))