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

@router.get("/", response_model=List[schemas.CartItem])
def get_cart(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == username).first()
    cart_items = db.query(models.Cart).filter(models.Cart.user_id == user.id).all()
    return cart_items

@router.post("/")
def add_to_cart(cart_item: schemas.CartItem, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == username).first()
    db_item = models.Cart(user_id=user.id, **cart_item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{cart_item_id}")
def remove_from_cart(cart_item_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == username).first()
    db_item = db.query(models.Cart).filter(models.Cart.id == cart_item_id, models.Cart.user_id == user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item removed from cart"}
