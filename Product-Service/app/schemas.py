# app/schemas.py
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional

class ProductBase(BaseModel):
    name: str = Field(..., example="Kaffeemaschine")
    description: Optional[str] = None
    price: Decimal = Field(..., example="199.99")
    details: Optional[str] = None
    count: int = Field(..., ge=0, example=10)
    imageLink: Optional[str] = Field(None, alias="imageLink", max_length=1024)

    class Config:
        allow_population_by_field_name = True

class ProductCreate(ProductBase):
    pass  # für jetzt identisch mit Base — separiert aber Intent (Create)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    details: Optional[str] = None
    count: Optional[int] = None
    imageLink: Optional[str] = None

class ProductRead(ProductBase):
    id: int

    class Config:
        orm_mode = True  # erlaubt Rückgabe von ORM-Objekten direkt
