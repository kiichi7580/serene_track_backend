import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# 環境を取得
env = os.getenv('ENV')

# データベースURLを取得
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

# スキーマを取得
schema = os.getenv('SCHEMA')

print(f'現在の環境は {env} です')
print(f'DATABASE_URL: {SQLALCHEMY_DATABASE_URL}')
print(f'スキーマは {env} です')

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'options': f'-csearch_path={schema}'})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()