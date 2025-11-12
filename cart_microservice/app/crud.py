from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app import models, schemas

def get_or_create_cart(db: Session, user_id: int, username: str):
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if cart:
        # Update username if it changed
        if cart.username != username:
            cart.username = username
            db.commit()
            db.refresh(cart)
        return cart
    cart = models.Cart(user_id=user_id, username=username)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart

def add_item(db: Session, user_id: int, username: str, product_id: int, product_name: str, 
             product_price: float, quantity: int, image_link: str = None):
    cart = get_or_create_cart(db, user_id, username)
    
    # Check if item already exists in cart
    item = db.query(models.CartItem).filter_by(
        cart_id=cart.id, 
        product_id=product_id
    ).first()
    
    if item:
        # Update existing item
        item.quantity += quantity
        item.product_name = product_name  # Update in case name/price changed
        item.product_price = product_price
        if image_link:
            item.image_link = image_link
    else:
        # Create new item
        item = models.CartItem(
            cart_id=cart.id,
            product_id=product_id,
            product_name=product_name,
            product_price=product_price,
            image_link=image_link,
            quantity=quantity
        )
        db.add(item)
    
    db.commit()
    db.refresh(item)
    return item

def update_item_quantity(db: Session, user_id: int, product_id: int, quantity: int):
    cart = db.query(models.Cart).filter_by(user_id=user_id).first()
    if not cart:
        return None
    
    item = db.query(models.CartItem).filter_by(cart_id=cart.id, product_id=product_id).first()
    if not item:
        return None
    
    if quantity <= 0:
        db.delete(item)
        db.commit()
        return None
    else:
        item.quantity = quantity
        db.commit()
        db.refresh(item)
        return item

def remove_item(db: Session, user_id: int, product_id: int):
    cart = db.query(models.Cart).filter_by(user_id=user_id).first()
    if not cart:
        return False
    
    item = db.query(models.CartItem).filter_by(cart_id=cart.id, product_id=product_id).first()
    if not item:
        return False
    
    db.delete(item)
    db.commit()
    return True

def get_cart(db: Session, user_id: int):
    return db.query(models.Cart).filter_by(user_id=user_id).first()

def clear_cart(db: Session, user_id: int):
    cart = db.query(models.Cart).filter_by(user_id=user_id).first()
    if not cart:
        return False
    
    # Delete all items
    db.query(models.CartItem).filter_by(cart_id=cart.id).delete()
    db.commit()
    return True

# Helper function to calculate totals
def calculate_cart_totals(cart):
    """Calculate total amounts for cart and its items"""
    total_amount = 0
    
    for item in cart.items:
        item_total = item.product_price * item.quantity
        total_amount += item_total
        # Add total_amount as a dynamic property to the item
        item.total_amount = item_total
    
    cart.total_amount = total_amount
    return cart