# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas, mapper
from decimal import Decimal

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def list_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product_in: schemas.ProductCreate):
    payload = mapper.create_to_model(product_in)
    product = models.Product(**payload)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update_product(db: Session, product: models.Product, updates: schemas.ProductUpdate):
    # Für jedes Feld, das nicht None ist, setzen wir das Model-Feld
    data = updates.dict(exclude_unset=True)
    if "imageLink" in data:
        data["image_link"] = data.pop("imageLink")
    for key, value in data.items():
        setattr(product, key, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product: models.Product):
    db.delete(product)
    db.commit()
    return


"""
Wichtig:

db.commit() schreibt Änderungen; db.refresh() lädt aktualisierte Daten (inkl. vom DB generierte Felder wie id).

exclude_unset=True bei updates.dict() sorgt dafür, dass nur geänderte Felder aktualisiert werden.

"""