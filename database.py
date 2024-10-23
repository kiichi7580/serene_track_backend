import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()


# 環境変数を取得
env = os.getenv('ENV', 'development')
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')
schema = os.getenv('SCHEMA', 'serene_track_dev')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'


if DEBUG:
    print("デバッグモードで実行中")
else:
    print("本番モードで実行中")


if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL が設定されていません")


print(f'現在の環境は {env} です')
print(f'DATABASE_URL: {SQLALCHEMY_DATABASE_URL}')
print(f'スキーマは {schema} です')

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, execution_options={"schema_translate_map": {None: schema}})
except Exception as e:
    print(f"データベースへの接続に失敗しました: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()