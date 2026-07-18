import sys
import os
import csv
from datetime import datetime

# Adjust sys.path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from database import engine, Base, SessionLocal
from models import User, Order, Payment, Feedback, Product

def get_emoji_for_category(category: str, item_name: str) -> str:
    cat = category.lower()
    name = item_name.lower()

    if "ice" in cat or "ice" in name:
        return "🍦" if "vanilla" in name or "cup" in name else ("🥭" if "mango" in name else "🍨")
    if "chip" in cat or "chip" in name or "namkeen" in cat:
        return "🥔" if "lays" in name or "bingo" in name else "🥨"
    if "soft drink" in cat or "drink" in cat or "water" in cat:
        return "🥤" if "cola" in name or "pepsi" in name else ("🍾" if "sprite" in name else "💧")
    if "toffee" in cat or "choc" in cat or "chocolate" in cat:
        return "🍫" if "dairy milk" in name or "kitkat" in name else "🍬"
    if "biscuit" in cat or "cookie" in cat:
        return "🍪"
    if "noodle" in cat or "maggi" in name:
        return "🍜"
    if "juice" in cat:
        return "🧃"
    if "dairy" in cat:
        return "🥛" if "milk" in name else ("🧈" if "butter" in name else "🧀")
    if "electr" in cat or "keyb" in name or "mouse" in name:
        return "⌨️" if "keyb" in name else ("🖱️" if "mouse" in name else "🔌")
    if "headp" in name or "audio" in cat:
        return "🎧"
    if "bag" in name or "pack" in name:
        return "🎒"

    return "📦"

def load_products_from_csv(csv_path: str, start_id: int) -> list:
    products = []
    if not os.path.exists(csv_path):
        print(f"Warning: CSV file not found at {csv_path}")
        return products

    current_id = start_id
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sku = row.get("SKU", f"SKU{current_id:03d}").strip()
            category = row.get("Category", "General").strip()
            item_name = row.get("ItemName", "").strip()
            qty_stock = int(row.get("QuantityInStock", 50))
            unit_price = float(row.get("UnitPriceINR", 99.0))
            brand = row.get("Brand", category).strip()

            desc = f"Brand: {brand} | Category: {category} | In Stock: {qty_stock} units"
            image = get_emoji_for_category(category, item_name)

            p = Product(
                id=current_id,
                sku=sku,
                name=item_name,
                price=unit_price,
                category=category,
                brand=brand,
                stock=qty_stock,
                description=desc,
                image=image
            )
            products.append(p)
            current_id += 1

    return products

def seed_db():
    print("Initializing Database Schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 1. Seed Users
        users = [
            User(id=1, name="John", email="john@test.com", password="123456"),
            User(id=2, name="Alice", email="alice@test.com", password="password"),
            User(id=3, name="Bob", email="bob@test.com", password="abc123")
        ]
        db.add_all(users)
        db.commit()
        print("Users seeded successfully.")

        # 2. Seed Products from inventory.csv and additional_inventory.csv
        db_dir = os.path.dirname(os.path.abspath(__file__))
        base_csv = os.path.join(db_dir, "inventory.csv")
        additional_csv = os.path.join(db_dir, "additional_inventory.csv")

        # Fallback if inventory.csv not present
        if not os.path.exists(base_csv):
            alt_base = os.path.join(db_dir, "local_grocery_food_inventory.csv")
            if os.path.exists(alt_base):
                base_csv = alt_base

        base_products = load_products_from_csv(base_csv, start_id=1)
        next_id = len(base_products) + 1
        add_products = load_products_from_csv(additional_csv, start_id=next_id)

        all_products = base_products + add_products
        db.add_all(all_products)
        db.commit()
        print(f"Loaded and seeded {len(all_products)} products from CSV files ({len(base_products)} from base inventory.csv, {len(add_products)} from additional_inventory.csv).")

        # 3. Seed Orders
        orders = [
            Order(id=101, user_id=1, product="Mechanical RGB Keyboard", quantity=1, amount=1999.0, status="Delivered", date=datetime(2026, 7, 10, 10, 30)),
            Order(id=102, user_id=1, product="Precision Wireless Optical Mouse", quantity=1, amount=899.0, status="Pending", date=datetime(2026, 7, 15, 14, 20)),
            Order(id=103, user_id=1, product="Adjustable Ergonomic Laptop Stand", quantity=1, amount=1599.0, status="Paid", date=datetime(2026, 7, 17, 16, 45)),
            Order(id=104, user_id=1, product="Amul Mango Duet Ice Cream 100ml", quantity=2, amount=90.0, status="Delivered", date=datetime(2026, 7, 18, 8, 15)),
            Order(id=105, user_id=2, product="Wireless Noise Cancelling Headphones", quantity=1, amount=2999.0, status="Delivered", date=datetime(2026, 7, 12, 11, 00)),
        ]
        db.add_all(orders)
        db.commit()
        print("Orders seeded successfully.")

        # 4. Seed Payments
        payments = [
            Payment(id="P101", order_id=101, method="Visa", status="Paid", amount=1999.0, date=datetime(2026, 7, 10, 10, 32)),
            Payment(id="P103", order_id=103, method="Mastercard", status="Paid", amount=1599.0, date=datetime(2026, 7, 17, 16, 46)),
            Payment(id="P104", order_id=104, method="Visa", status="Paid", amount=90.0, date=datetime(2026, 7, 18, 8, 16))
        ]
        db.add_all(payments)
        db.commit()
        print("Payments seeded successfully.")

        # 5. Seed Feedbacks
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
