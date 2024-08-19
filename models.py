from database import Base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey


class Users(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, unique=True)
  email = Column(String, unique=True)
  created_at = Column(TIMESTAMP)
  birth_date = Column(TIMESTAMP)
  photo_url = Column(String)
  short_term_goal = Column(String, nullable=True)
  long_term_goal = Column(String, nullable=True)
  hashed_password = Column(String)
  is_active = Column(Boolean, default=True)
  role = Column(String)
  health_data_integration_status = Column(Boolean, default=False, server_default="false")


class Todos(Base):
  __tablename__ = 'todos'

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String)
  description = Column(String)
  complete = Column(Boolean, default=False)
  category_id = Column(String)
  # notification_time = Column(TIMESTAMP)
  created_at = Column(TIMESTAMP)
  owner_id = Column(Integer, ForeignKey("users.id"))