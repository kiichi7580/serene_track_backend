from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

class Todos(Base):
  __tablename__ = 'todos'

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String)
  description = Column(String)
  complete = Column(Boolean, default=False)
  category_id = Column(String)
  date = Column(DateTime, default=func.now())
  user_id = Column(String)