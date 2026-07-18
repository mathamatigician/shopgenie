from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import re

from database import get_db
from models import Feedback, Order, User
from auth import get_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback"])

class FeedbackRequest(BaseModel):
    message: str
    order_id: Optional[int] = None

class FeedbackResponse(BaseModel):
    id: int
    order_id: Optional[int]
    message: str
    sentiment: str
    category: str
    urgency: str
    keywords: Optional[str]
    reply: str
    created_at: datetime

def analyze_feedback_text(text: str):
    text_lower = text.lower()
    
    # Sentiment Analysis
    negative_words = ["bad", "poor", "terrible", "broken", "crushed", "horrible", "damaged", "delay", "late", "worst", "defective", "disappointed", "dissatisfied"]
    positive_words = ["great", "good", "excellent", "awesome", "loved", "best", "satisfied", "amazing", "fast", "perfect", "superb"]
    
    neg_score = sum(1 for word in negative_words if word in text_lower)
    pos_score = sum(1 for word in positive_words if word in text_lower)
    
    if neg_score > pos_score:
        sentiment = "Negative"
    elif pos_score > neg_score:
        sentiment = "Positive"
    else:
        sentiment = "Neutral"

    # Category Detection
    category = "General"
    if any(k in text_lower for k in ["packag", "box", "wrap", "container", "crushed", "carton"]):
        category = "Packaging"
    elif any(k in text_lower for k in ["quality", "material", "defective", "broken", "durability", "working"]):
        category = "Quality"
    elif any(k in text_lower for k in ["delivery", "ship", "arrive", "late", "delay", "courier"]):
        category = "Delivery"
    elif any(k in text_lower for k in ["support", "service", "agent", "help"]):
        category = "Customer Service"
    elif any(k in text_lower for k in ["product", "item", "keyboard", "mouse", "stand"]):
        category = "Product"

    # Urgency Detection
    if sentiment == "Negative" and (any(k in text_lower for k in ["crushed", "broken", "damaged", "terrible", "urgent", "refund", "replace"]) or neg_score >= 2):
        urgency = "High"
    elif sentiment == "Negative":
        urgency = "Medium"
    else:
        urgency = "Low"

    # Extract Keywords
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text_lower)
    stop_words = {"this", "that", "with", "from", "have", "were", "your", "very", "what", "will"}
    extracted = [w for w in words if w not in stop_words][:5]
    keywords_str = ", ".join(set(extracted))

    # Generate empathetic response
    if sentiment == "Negative":
        reply = f"We're deeply sorry to hear about your experience regarding the {category.lower()}. We've flagged this with High Priority (Urgency: {urgency}) to ensure our team addresses it immediately."
    elif sentiment == "Positive":
        reply = f"Thank you so much for your positive feedback! We're thrilled that you are satisfied with your purchase."
    else:
        reply = "Thank you for sharing your feedback with us! We continuously strive to improve our service."

    return {
        "sentiment": sentiment,
        "category": category,
        "urgency": urgency,
        "keywords": keywords_str,
        "reply": reply
    }

@router.get("", response_model=List[dict])
def get_feedbacks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    feedbacks = db.query(Feedback).filter(Feedback.user_id == current_user.id).order_by(Feedback.id.desc()).all()
    res = []
    for f in feedbacks:
        res.append({
            "id": f.id,
            "order_id": f.order_id,
            "message": f.message,
            "sentiment": f.sentiment,
            "category": f.category,
            "urgency": f.urgency,
            "keywords": f.keywords,
            "created_at": f.created_at
        })
    return res

@router.post("")
def submit_feedback(request: FeedbackRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analysis = analyze_feedback_text(request.message)
    
    order_id = request.order_id
    if not order_id:
        # Check if text mentions an order ID like #101 or order 101
        match = re.search(r'order\s*#?(\d+)', request.message, re.IGNORECASE)
        if match:
            order_id = int(match.group(1))
        else:
            # Find latest order of user
            latest_order = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.id.desc()).first()
            if latest_order:
                order_id = latest_order.id

    fb = Feedback(
        order_id=order_id,
        user_id=current_user.id,
        message=request.message,
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
        "reply": analysis["reply"]
    }
