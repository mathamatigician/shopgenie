from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    orders = relationship("Order", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image = Column(String, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    amount = Column(Float, nullable=False)
    status = Column(String, default="Pending") # Pending, Paid, Delivered
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    payments = relationship("Payment", back_populates="order")
    feedbacks = relationship("Feedback", back_populates="order")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True) # e.g. P101
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    method = Column(String, default="Visa") # Visa, Mastercard, UPI, Card
    status = Column(String, default="Paid") # Paid, Pending, Refunded
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="payments")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    sentiment = Column(String, default="Neutral") # Positive, Negative, Neutral
    category = Column(String, default="General") # Packaging, Quality, Delivery, Product
    urgency = Column(String, default="Low") # Low, Medium, High
    keywords = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedbacks")
    order = relationship("Order", back_populates="feedbacks")
