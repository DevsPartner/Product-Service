# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# DB URL aus Umgebungsvariable lesen, Standard fallback (postgres)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/products_db")

# Engine erstellen – verbindet uns mit der DB
engine = create_engine(DATABASE_URL, echo=True, future=True)

# Session factory – erzeugt DB-Sessions (Transaktionen)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Base-Klasse für Modelle (Models erben von Base)
Base = declarative_base()

# Dependency für FastAPI: liefert eine DB-Session pro Request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

