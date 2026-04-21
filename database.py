from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,         # verify connection before use
    pool_size=10,
    max_overflow=20,
    echo=settings.APP_ENV == "development",
)

# Enable full-text search support for MySQL
@event.listens_for(engine, "connect")
def set_mysql_options(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET NAMES utf8mb4")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Dependency: yields a DB session and always closes it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()