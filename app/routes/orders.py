from dotenv import load_dotenv
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

router = APIRouter()
load_dotenv()

# Retrieve SECRET_KEY from .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

@router.post("/")
def place_order(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == username).first()
    cart_items = db.query(models.Cart).filter(models.Cart.user_id == user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_price = sum(item.quantity * db.query(models.Book).filter(models.Book.id == item.book_id).first().price for item in cart_items)
    
    order = models.Order(user_id=user.id, total_price=total_price, status="pending")
    db.add(order)
    db.commit()

    for item in cart_items:
        book = db.query(models.Book).filter(models.Book.id == item.book_id).first()
        if book.quantity_available < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for book {book.title}")
        book.quantity_available -= item.quantity
        db.delete(item)

    db.commit()
    return {"message": "Order placed successfully", "order_id": order.id}

@router.get("/", response_model=List[schemas.Order])
def get_orders(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == username).first()
    orders = db.query(models.Order).filter(models.Order.user_id == user.id).all()
    return orders
