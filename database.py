from sqlalchemy.orm import sessionmaker,DeclarativeBase
from sqlalchemy import create_engine

database_url = "database url"

engine = create_engine(
    database_url,
    pool_pre_ping=True #handles stabel db connection
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit = False
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    
        

class Base(DeclarativeBase):
    pass