from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Payment, Order, User
from auth import get_current_user

router = APIRouter(tags=["Payments"])

class PaymentRequest(BaseModel):
    order_id: int
    method: Optional[str] = "Visa"

class PaymentResponse(BaseModel):
    id: str
    order_id: int
    method: str
    status: str
    amount: float
    date: datetime

    class Config:
        orm_mode = True

@router.get("/payments", response_model=List[PaymentResponse])
def get_payments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payments = db.query(Payment).join(Order).filter(Order.user_id == current_user.id).order_by(Payment.date.desc()).all()
    return payments

@router.post("/payment", response_model=dict)
def process_payment(request: PaymentRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == request.order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{request.order_id} not found for user")

    if order.status == "Paid":
        return {"status": "Already Paid", "message": f"Order #{order.id} is already paid.", "payment_id": f"P{order.id}"}

    payment_id = f"P{order.id}"
    
    # Check if payment record exists
    existing_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not existing_payment:
        new_payment = Payment(
            id=payment_id,
            order_id=order.id,
            method=request.method,
            status="Paid",
            amount=order.amount,
            date=datetime.utcnow()
        )
        db.add(new_payment)
    else:
        existing_payment.status = "Paid"

    order.status = "Paid"
    db.commit()

    return {
        "status": "Success",
        "message": f"Payment of ₹{order.amount:.2f} successful for Order #{order.id}.",
        "payment_id": payment_id,
        "amount": order.amount
    }
