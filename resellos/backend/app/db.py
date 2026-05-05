from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

def _create_engine():
    try:
        return create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    except ModuleNotFoundError:
        return create_engine("sqlite:///./resellos.local.db", connect_args={"check_same_thread": False})


engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
