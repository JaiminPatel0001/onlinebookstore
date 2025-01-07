from dotenv import load_dotenv
import os
from datetime import datetime
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
# from typing import Any

router = APIRouter()
load_dotenv()

# Retrieve SECRET_KEY from .env
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment variables.")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "exp" in payload and datetime.datetime.utcnow() > datetime.datetime.utcfromtimestamp(payload["exp"]):
            raise HTTPException(status_code=401, detail="Token has expired")
        if "type" not in payload or payload["type"] != "Admin":
            raise HTTPException(status_code=403, detail="Not authorized as admin")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token:")
    



@router.get("/", response_model=List[schemas.Book], operation_id="list_books")
def list_books(db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return books


@router.post("/", response_model=schemas.Book, operation_id="add_book")
def add_book(book: schemas.Book, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.put("/{book_id}", response_model=schemas.Book, operation_id="update_book")
def update_book(book_id: int, book: schemas.Book, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/{book_id}", operation_id="delete_book")
def delete_book(book_id: int, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}