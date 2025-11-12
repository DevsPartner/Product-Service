# app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class CartItemCreate(BaseModel):
    product_id: int
    product_name: str
    product_price: float = Field(..., gt=0)
    image_link: Optional[str] = None
    quantity: int = Field(..., gt=0)

class CartItemUpdate(BaseModel):  # Add this missing schema
    quantity: int = Field(..., gt=0)

class CartItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    image_link: Optional[str]
    quantity: int
    total_amount: float  # Calculated field

    class Config:
        from_attributes = True  # Use this instead of orm_mode for Pydantic v2

class CartRead(BaseModel):
    id: int
    user_id: int
    username: str
    items: List[CartItemRead] = []
    total_amount: float  # Calculated field for entire cart

    class Config:
        from_attributes = True  # Use this instead of orm_mode for Pydantic v2

class CartCreate(BaseModel):
    user_id: int
    username: str