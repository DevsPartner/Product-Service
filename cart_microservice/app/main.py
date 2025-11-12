# app/main.py
from fastapi import FastAPI

app = FastAPI(title="Cart Service", version="1.0.0")

@app.get("/")
def root():
    return {"status": "Cart Service is running", "message": "Visit /docs for API documentation"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Import and include router after app creation to avoid circular imports
from app.routes import router
app.include_router(router, prefix="/api/v1")