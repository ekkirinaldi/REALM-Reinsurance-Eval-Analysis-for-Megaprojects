from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Define the database URL
DATABASE_URL = "sqlite:///realm.db"

# Create an engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
