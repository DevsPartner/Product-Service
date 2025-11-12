from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Cart Service (Postgres)")

@app.get("/")
def root():
    return {"status": "Cart Service is running"}

app.include_router(router)