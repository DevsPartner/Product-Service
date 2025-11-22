# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from . import models, schemas, crud, mapper
from .database import engine, Base, get_db
from fastapi.middleware.cors import CORSMiddleware

# Tabellen erstellen, falls noch nicht vorhanden (nur für Entwicklung; in Prod evtl. migrations verwenden)
Base.metadata.create_all(bind=engine)
origins = [
    "http://localhost:3000",
    "http://123.0.0.1:3000",
]
app = FastAPI(title="Product Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # wichtig für cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Product Service läuft erfolgreich 🚀"}



@app.post("/products/", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    """
    Endpoint um ein Produkt zu erstellen.
    product_in wird durch Pydantic validiert.
    """
    product = crud.create_product(db=db, product_in=product_in)
    return mapper.model_to_read(product)

@app.get("/products/{product_id}", response_model=schemas.ProductRead)
def get_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return mapper.model_to_read(product)

@app.get("/products/", response_model=List[schemas.ProductRead])
def list_products_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.list_products(db, skip=skip, limit=limit)
    return [mapper.model_to_read(p) for p in products]

@app.patch("/products/{product_id}", response_model=schemas.ProductRead)
def update_product_endpoint(product_id: int, updates: schemas.ProductUpdate, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    updated = crud.update_product(db, product, updates)
    return mapper.model_to_read(updated)

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    crud.delete_product(db, product)
    return None
