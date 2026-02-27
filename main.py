from fastapi import FastAPI

from app.db import Base, engine
from app.routers import auth, cart, orders, products

app = FastAPI(title="E-Commerce API")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
