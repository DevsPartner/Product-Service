# app/models.py
from sqlalchemy import Column, Integer, BigInteger, String, Numeric, Text
from sqlalchemy.orm import relationship
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(12, 2), nullable=False)  # Decimal-like storage
    details = Column(Text, nullable=True)
    count = Column(Integer, nullable=False, default=0)
    image_link = Column(String(1024), nullable=True)




#Erklärung wichtige Zeilen:

#__tablename__ = "products": Name der DB-Tabelle.

#id = Column(BigInteger, primary_key=True, ...): Long in deiner Spezifikation → BigInteger. autoincrement=True erzeugt automatisch IDs.

#price = Column(Numeric(12, 2)): speichert monetäre Werte exakt; in Python nutzen wir Decimal.

#index=True bei Feldern, die häufig durchsucht werden (z. B. name, id) — verbessert Performance für SELECTs.


