import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# 環境を取得 (デフォルトは development)
env = os.getenv('ENV', 'development')

# 環境ごとの .env ファイルを読み込む
if env == 'development':
    load_dotenv(dotenv_path='.env.development')
elif env == 'production':
    load_dotenv(dotenv_path='.env.production')

# データベースURLを取得
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

print(f'現在の環境は {env} です')
print(f'DATABASE_URL: {SQLALCHEMY_DATABASE_URL}')

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'options': '-csearch_path=serene_track'})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()