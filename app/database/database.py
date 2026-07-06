from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from app.config.settings import settings
from sqlalchemy.orm import Session

# Build the DSN explicitly so oracledb thin driver uses service_name,
# not SID. SQLAlchemy's URL parser can misroute the path component as
# a SID when using oracle+oracledb://, so we pass connect_args directly.
engine = create_engine(
    "oracle+oracledb://",
    connect_args={
        "user": settings.DB_USER,
        "password": settings.DB_PASSWORD,
        "dsn": settings.DB_DSN,   # e.g. localhost:1521/freepdb1
    },
    pool_pre_ping=True
)

DATABASE_URL = f"oracle+oracledb://{settings.DB_USER}:***@{settings.DB_DSN}"

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

Base = declarative_base()