# app/prepare_db.py
from app.database import Base, engine
from app import models

def main():
    print("Creating database tables (if not exist)...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    main()