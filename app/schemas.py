from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum
from datetime import datetime

class UserTypeEnum(str, Enum):
    Admin = "Admin"
    Customer = "Customer"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    type: UserTypeEnum

class UserLogin(BaseModel):
    username: str
    password: str
 
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    type: UserTypeEnum

    class Config:
        from_attributes = True

class Book(BaseModel):
    id: int
    title: str
    author: str
    price: float
    quantity_available: int

    class Config:
        from_attributes = True

class CartItem(BaseModel):
    id: int
    user_id: int
    book_id: int
    quantity: int

    class Config:
        from_attributes = True

class Order(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str