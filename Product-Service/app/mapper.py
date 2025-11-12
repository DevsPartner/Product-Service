# app/mapper.py
from .models import Product
from .schemas import ProductRead, ProductCreate
from decimal import Decimal

def model_to_read(product: Product) -> ProductRead:
    """
    Konvertiert ein SQLAlchemy Product -> ProductRead DTO.
    """
    return ProductRead(
        id=product.id,
        name=product.name,
        description=product.description,
        price=Decimal(product.price),
        details=product.details,
        count=product.count,
        imageLink=product.image_link
    )

def create_to_model(dto: ProductCreate) -> dict:
    """
    Mappt ProductCreate DTO zu einem dict, das in ein DB-Model passt.
    Wir geben ein dict zurück, weil SQLAlchemy-Model-Init bevorzugt kwargs verwendet.
    """
    return {
        "name": dto.name,
        "description": dto.description,
        "price": dto.price,
        "details": dto.details,
        "count": dto.count,
        "image_link": dto.imageLink
    }


"""
Warum Mapper?

Trennung von Domänen-Modell (DB) und API-DTOs. 

So ist dein API-Schema unabhängig von DB-Feldern (z.B. imageLink vs image_link).

create_to_model liefert ein dict, das direkt an Product(**dict) benutzt werden kann

"""