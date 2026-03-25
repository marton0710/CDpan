from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./Smart_Signing_Guardian.db"

engine = create_engine(
    url=DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """打开数据库"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
