from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:root@192.168.1.2:5432/onlinebookstore"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()


# def test_connection():
#     try:
#         with engine.connect() as connection:
#             print("Database connection successful!")
#     except Exception as e:
#         print("Database connection failed!")
#         print(f"Error: {e}")