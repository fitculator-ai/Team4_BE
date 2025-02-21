from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import create_engine
from app.config import DATABASE_URL
from sqlalchemy import text

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# DB 세션 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

