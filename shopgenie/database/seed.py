import sys
import os
from datetime import datetime

# Adjust sys.path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from database import engine, Base, SessionLocal
from models import User, Order, Payment, Feedback, Product

def seed_db():
    print("Initializing Database Schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Seed Users
        users = [
            User(id=1, name="John", email="john@test.com", password="123456"),
            User(id=2, name="Alice", email="alice@test.com", password="password"),
            User(id=3, name="Bob", email="bob@test.com", password="abc123")
        ]
        db.add_all(users)
        db.commit()
        print("Users seeded successfully.")

        # Seed Products
        products = [
            Product(id=1, name="Keyboard", price=1999.0, category="Electronics", description="Ergonomic mechanical keyboard with RGB backlighting.", image="⌨️"),
            Product(id=2, name="Mouse", price=899.0, category="Electronics", description="Precision wireless optical mouse with ergonomic grip.", image="🖱️"),
            Product(id=3, name="Laptop Stand", price=1599.0, category="Accessories", description="Adjustable aluminum laptop stand for ergonomic working.", image="💻"),
            Product(id=4, name="Laptop Bag", price=1299.0, category="Accessories", description="Water-resistant stylish laptop backpack with padded compartment.", image="🎒"),
            Product(id=5, name="Wireless Headphones", price=2999.0, category="Audio", description="Noise-cancelling over-ear wireless headphones.", image="🎧"),
            Product(id=6, name="USB-C Hub", price=1499.0, category="Electronics", description="7-in-1 multi-port adapter with 4K HDMI and USB 3.0.", image="🔌"),
            Product(id=7, name="Desk Mat", price=499.0, category="Accessories", description="Large non-slip waterproof desk pad.", image="📐")
        ]
        db.add_all(products)
        db.commit()
        print("Products seeded successfully.")

        # Seed Orders
        orders = [
            Order(id=101, user_id=1, product="Keyboard", quantity=1, amount=1999.0, status="Delivered", date=datetime(2026, 7, 10, 10, 30)),
            Order(id=102, user_id=1, product="Mouse", quantity=1, amount=899.0, status="Pending", date=datetime(2026, 7, 15, 14, 20)),
            Order(id=103, user_id=1, product="Laptop Stand", quantity=1, amount=1599.0, status="Paid", date=datetime(2026, 7, 17, 16, 45)),
            Order(id=104, user_id=2, product="Wireless Headphones", quantity=1, amount=2999.0, status="Delivered", date=datetime(2026, 7, 12, 11, 00)),
        ]
        db.add_all(orders)
        db.commit()
        print("Orders seeded successfully.")

        # Seed Payments
        payments = [
            Payment(id="P101", order_id=101, method="Visa", status="Paid", amount=1999.0, date=datetime(2026, 7, 10, 10, 32)),
            Payment(id="P103", order_id=103, method="Mastercard", status="Paid", amount=1599.0, date=datetime(2026, 7, 17, 16, 46))
        ]
        db.add_all(payments)
        db.commit()
        print("Payments seeded successfully.")

        # Seed Feedbacks
        feedbacks = [
            Feedback(
                id=1,
                order_id=101,
                user_id=1,
                message="Packaging was poor. Box arrived crushed.",
                sentiment="Negative",
                category="Packaging",
                urgency="High",
                keywords="packaging, crushed, poor"
            )
        ]
        db.add_all(feedbacks)
        db.commit()
        print("Feedbacks seeded successfully.")

        print("Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
