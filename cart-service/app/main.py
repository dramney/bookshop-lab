from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, redis
from fastapi.middleware.cors import CORSMiddleware
from .events import publish_event
from .db import Base, engine, SessionLocal
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import json

# Minimal persistent CartItem model
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
Base.metadata.create_all(bind=engine)

# Simple DB model inline (for brevity)
from sqlalchemy import Integer, Column, String
from .db import Base

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    book_id = Column(String)
    quantity = Column(Integer)

app = FastAPI(title="cart-service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Порт React застосунку
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

class ItemIn(BaseModel):
    bookId: str
    quantity: int

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/api/cart/{user_id}/items")
def add_item(user_id: str, item: ItemIn, db: Session = next(get_db())):
    # Update Redis cache
    key = f"cart:{user_id}"
    cart = r.hgetall(key) or {}
    current = int(cart.get(item.bookId, 0))
    new_q = current + item.quantity
    r.hset(key, item.bookId, new_q)
    # Persist
    try:
        ci = CartItem(user_id=user_id, book_id=item.bookId, quantity=new_q)
        db.add(ci); db.commit()
    except SQLAlchemyError:
        db.rollback()
    # Publish event
    publish_event({"type":"ItemAddedToCart","userId":user_id,"bookId":item.bookId,"quantity":item.quantity})
    return {"status":"ok"}

@app.get("/api/cart/{user_id}")
def get_cart(user_id: str):
    key = f"cart:{user_id}"
    cart = r.hgetall(key) or {}
    # convert quantities to int
    return {k: int(v) for k,v in cart.items()}
