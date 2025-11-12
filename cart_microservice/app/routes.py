# app/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import schemas and crud inside the functions to avoid circular imports
@router.get("/test")
def test_endpoint():
    return {"message": "API is working!"}

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.post("/cart/{user_id}/items", status_code=status.HTTP_201_CREATED)
def add_to_cart(
    user_id: int, 
    username: str,
    db: Session = Depends(get_db)
):
    from app import schemas, crud
    # For now, just return a simple response to test
    return {"message": "Add to cart endpoint", "user_id": user_id, "username": username}

@router.put("/cart/{user_id}/items/{product_id}")
def update_quantity(
    user_id: int, 
    product_id: int, 
    db: Session = Depends(get_db)
):
    return {"message": "Update quantity endpoint", "user_id": user_id, "product_id": product_id}

@router.delete("/cart/{user_id}/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(user_id: int, product_id: int, db: Session = Depends(get_db)):
    return

@router.get("/cart/{user_id}")
def read_cart(user_id: int, db: Session = Depends(get_db)):
    from app import crud
    cart = crud.get_cart(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Calculate totals
    cart = crud.calculate_cart_totals(cart)
    return cart

@router.delete("/cart/{user_id}/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(user_id: int, db: Session = Depends(get_db)):
    return

@router.post("/cart/")
def create_cart(db: Session = Depends(get_db)):
    return {"message": "Create cart endpoint"}