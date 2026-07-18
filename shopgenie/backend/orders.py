from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Order, Product, User
from auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

class OrderCreateRequest(BaseModel):
    product: str
    quantity: int = 1
    amount: Optional[float] = None

class OrderResponse(BaseModel):
    id: int
    user_id: int
    product: str
    quantity: int
    amount: float
    status: str
    date: datetime

    class Config:
        orm_mode = True

@router.get("", response_model=List[OrderResponse])
def get_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.id.desc()).all()
    return orders

@router.post("", response_model=OrderResponse)
def create_order(request: OrderCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Calculate amount if not provided
    amount = request.amount
    if not amount:
        # Match product in DB or default price
        prod = db.query(Product).filter(Product.name.ilike(f"%{request.product}%")).first()
        if prod:
            amount = prod.price * request.quantity
        else:
            amount = 999.0 * request.quantity

    # Generate new order ID starting after existing max
    max_id = db.query(Order.id).order_by(Order.id.desc()).first()
    new_id = (max_id[0] + 1) if max_id and max_id[0] else 104

    new_order = Order(
        id=new_id,
        user_id=current_user.id,
        product=request.product.title(),
        quantity=request.quantity,
        amount=amount,
        status="Pending",
        date=datetime.utcnow()
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order
