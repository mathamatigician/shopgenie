from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import re

from models import Order, Payment, Feedback, Product, User
from feedback import analyze_feedback_text

def tool_search_products(db: Session, query: str) -> List[Dict[str, Any]]:
    """
    Searches the product catalog for items matching keywords in the query.
    """
    stop_words = {"create", "new", "order", "for", "each", "brand", "only", "want", "need", "buy", "a", "an", "the", "please", "list", "show", "items", "available"}
    terms = [t.strip().lower() for t in re.findall(r'\b[a-zA-Z0-9]+\b', query) if t.strip().lower() not in stop_words and len(t.strip()) > 1]

    all_products = db.query(Product).all()
    matches = []

    for p in all_products:
        p_name = p.name.lower()
        p_desc = (p.description or "").lower()
        p_cat = p.category.lower()

        score = 0
        for term in terms:
            if term in p_name:
                score += 4
            elif term in p_cat:
                score += 2
            elif term in p_desc:
                score += 1

        if score > 0:
            matches.append((score, p))

    matches.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "category": p.category,
            "description": p.description,
            "image": p.image
        } for _, p in matches
    ]


def tool_list_sorted_products(db: Session, query: str, sort_by: str = "price_asc") -> List[Dict[str, Any]]:
    """
    Lists catalog items matching query keywords and sorts them by price (price_asc / price_desc).
    """
    matches = tool_search_products(db, query)
    if not matches:
        all_prods = db.query(Product).all()
        matches = [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "category": p.category,
                "description": p.description,
                "image": p.image
            } for p in all_prods
        ]

    if sort_by == "price_asc":
        matches.sort(key=lambda x: x["price"])
    elif sort_by == "price_desc":
        matches.sort(key=lambda x: x["price"], reverse=True)

    return matches


def tool_get_filtered_orders(db: Session, user_id: int, filter_term: str) -> List[Dict[str, Any]]:
    """
    Retrieves orders placed by user matching a specific product filter or category (e.g. 'icecream', 'icecreams', 'keyboard').
    """
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.id.desc()).all()

    clean_filter = filter_term.lower()
    # Normalize plural & word variants (e.g. icecreams, ice-creams -> ice cream)
    clean_filter = clean_filter.replace("icecreams", "ice cream").replace("icecream", "ice cream").replace("ice-cream", "ice cream")

    ignore_words = {
        "list", "last", "past", "previous", "recent", "having", "with", "containing",
        "items", "item", "ordered", "orders", "order", "my", "show", "purchased",
        "history", "for", "of", "in"
    }

    clean_words = [w for w in re.findall(r'\b[a-zA-Z0-9]+\b', clean_filter) if w not in ignore_words and len(w) > 1]

    filtered = []
    for o in orders:
        o_prod = o.product.lower()
        if not clean_words:
            filtered.append({
                "id": o.id,
                "product": o.product,
                "quantity": o.quantity,
                "amount": o.amount,
                "status": o.status,
                "date": o.date.strftime("%Y-%m-%d %H:%M")
            })
        elif any(w in o_prod for w in clean_words) or ("ice" in clean_filter and "cream" in o_prod):
            filtered.append({
                "id": o.id,
                "product": o.product,
                "quantity": o.quantity,
                "amount": o.amount,
                "status": o.status,
                "date": o.date.strftime("%Y-%m-%d %H:%M")
            })

    return filtered


def tool_create_order(db: Session, user_id: int, product: str, quantity: int = 1) -> Dict[str, Any]:
    """
    Creates a new order for the user.
    """
    matched_product = db.query(Product).filter(Product.name.ilike(f"%{product}%")).first()
    if matched_product:
        product_name = matched_product.name
        unit_price = matched_product.price
    else:
        product_name = product.strip().title()
        unit_price = 1299.0

    total_amount = unit_price * max(1, quantity)

    max_id = db.query(Order.id).order_by(Order.id.desc()).first()
    new_order_id = (max_id[0] + 1) if max_id and max_id[0] else 104

    order = Order(
        id=new_order_id,
        user_id=user_id,
        product=product_name,
        quantity=quantity,
        amount=total_amount,
        status="Pending",
        date=datetime.utcnow()
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "order_id": order.id,
        "product": order.product,
        "quantity": order.quantity,
        "amount": order.amount,
        "status": order.status,
        "message": f"Order #{order.id} for {order.quantity}x '{order.product}' created successfully! Total: ₹{order.amount:.2f}. Status: Pending Payment."
    }


def tool_pay_order(db: Session, user_id: int, order_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Processes payment for a specific order or the user's latest pending order.
    """
    query = db.query(Order).filter(Order.user_id == user_id)
    if order_id:
        order = query.filter(Order.id == order_id).first()
    else:
        order = query.filter(Order.status == "Pending").order_by(Order.id.desc()).first()
        if not order:
            order = query.order_by(Order.id.desc()).first()

    if not order:
        return {
            "status": "Failed",
            "message": "No active order found to pay."
        }

    if order.status == "Paid":
        return {
            "order_id": order.id,
            "status": "Paid",
            "message": f"Order #{order.id} is already paid.",
            "payment_id": f"P{order.id}"
        }

    payment_id = f"P{order.id}"
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        payment = Payment(
            id=payment_id,
            order_id=order.id,
            method="Visa",
            status="Paid",
            amount=order.amount,
            date=datetime.utcnow()
        )
        db.add(payment)
    else:
        payment.status = "Paid"

    order.status = "Paid"
    db.commit()

    return {
        "order_id": order.id,
        "payment_id": payment_id,
        "amount": order.amount,
        "status": "Paid",
        "message": f"Payment of ₹{order.amount:.2f} completed successfully for Order #{order.id} using saved card (Visa)."
    }


def tool_submit_feedback(db: Session, user_id: int, message: str, order_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Submits user feedback, performs sentiment analysis, and returns details.
    """
    if not order_id:
        match = re.search(r'order\s*#?(\d+)', message, re.IGNORECASE)
        if match:
            order_id = int(match.group(1))
        else:
            latest_order = db.query(Order).filter(Order.user_id == user_id).order_by(Order.id.desc()).first()
            if latest_order:
                order_id = latest_order.id

    analysis = analyze_feedback_text(message)

    fb = Feedback(
        order_id=order_id,
        user_id=user_id,
        message=message,
        sentiment=analysis["sentiment"],
        category=analysis["category"],
        urgency=analysis["urgency"],
        keywords=analysis["keywords"],
        created_at=datetime.utcnow()
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    return {
        "feedback_id": fb.id,
        "order_id": fb.order_id,
        "sentiment": fb.sentiment,
        "category": fb.category,
        "urgency": fb.urgency,
        "keywords": fb.keywords,
        "reply": analysis["reply"],
        "message": f"Feedback logged (ID #{fb.id}). Sentiment: {fb.sentiment} | Category: {fb.category} | Urgency: {fb.urgency}. {analysis['reply']}"
    }


def tool_recommend_products(db: Session, user_id: int, query_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates intelligent product recommendations based on user order history and query hint.
    """
    past_orders = db.query(Order).filter(Order.user_id == user_id).all()
    ordered_product_names = [o.product.lower() for o in past_orders]

    all_products = db.query(Product).all()

    recommendations = []
    if query_hint and ("bag" in query_hint.lower() or "laptop bag" in query_hint.lower()):
        recs = [p for p in all_products if "bag" in p.name.lower()]
        if not recs:
            recs = [p for p in all_products if p.category == "Accessories"]
        recommendations = recs
    else:
        if any("keyboard" in p or "laptop" in p for p in ordered_product_names):
            recs = [p for p in all_products if p.name in ["Laptop Bag", "USB-C Hub", "Wireless Headphones", "Desk Mat"]]
        else:
            recs = all_products[:4]
        recommendations = recs

    formatted_recs = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "category": p.category,
            "description": p.description,
            "image": p.image
        } for p in recommendations
    ]

    return {
        "user_id": user_id,
        "recommendations": formatted_recs,
        "message": f"Based on your purchase history and interests, here are top recommendations for you:"
    }


def tool_get_orders(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Retrieves all orders for the given user.
    """
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.id.desc()).all()
    formatted = [
        {
            "id": o.id,
            "product": o.product,
            "quantity": o.quantity,
            "amount": o.amount,
            "status": o.status,
            "date": o.date.strftime("%Y-%m-%d %H:%M")
        } for o in orders
    ]
    return {
        "user_id": user_id,
        "count": len(formatted),
        "orders": formatted,
        "message": f"You have {len(formatted)} total order(s)."
    }
