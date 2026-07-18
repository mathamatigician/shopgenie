import os
import re
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from ai.tools import (
    tool_create_order,
    tool_pay_order,
    tool_submit_feedback,
    tool_recommend_products,
    tool_get_orders
)

class ShopGenieAgent:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Gemini client initialization failed: {e}")

    def process_message(self, user_message: str, user_id: int, user_name: str, db: Session) -> Dict[str, Any]:
        msg_lower = user_message.strip().lower()

        # 1. FEEDBACK INTENT (Checked first to capture phrases like "Packaging was poor for order 101")
        # Examples: "The product quality was bad", "Packaging was poor for order 101", "Great delivery", "It broke in 1 day"
        if any(k in msg_lower for k in ["quality", "packaging", "package", "broken", "crushed", "bad", "poor", "terrible", "feedback", "horrible", "damaged", "great", "awesome", "disappointed"]):
            order_id = self._extract_order_id(msg_lower)
            result = tool_submit_feedback(db, user_id=user_id, message=user_message, order_id=order_id)
            reply = f"*(Feedback Analyzed)* Sentiment: **{result['sentiment']}** | Category: **{result['category']}** | Urgency: **{result['urgency']}**\n\n{result['reply']}"
            return {
                "reply": reply,
                "tool_called": "submit_feedback",
                "tool_output": result,
                "data": {"feedback": result}
            }

        # 2. ORDER CREATION INTENT
        # Examples: "I want another keyboard", "Order another mouse", "Buy 2 laptop stands", "Order a laptop bag"
        if any(k in msg_lower for k in ["want", "order", "buy", "purchase", "need", "add"]) and not any(k in msg_lower for k in ["pay", "payment", "feedback", "recommend"]):
            product, qty = self._extract_product_and_qty(msg_lower)
            if product:
                result = tool_create_order(db, user_id=user_id, product=product, quantity=qty)
                reply = f"I've placed a new order for **{qty}x {result['product']}** (Order #{result['order_id']}) amounting to **₹{result['amount']:.2f}**. Status is currently **{result['status']}**. Would you like to pay for it now?"
                return {
                    "reply": reply,
                    "tool_called": "create_order",
                    "tool_output": result,
                    "data": {"order": result}
                }

        # 3. PAYMENT INTENT
        # Examples: "Pay using saved card", "Pay for my latest order", "Pay order 102", "Complete payment"
        if any(k in msg_lower for k in ["pay", "payment", "checkout", "settle"]):
            order_id = self._extract_order_id(msg_lower)
            result = tool_pay_order(db, user_id=user_id, order_id=order_id)
            if result.get("status") == "Paid":
                reply = f"Payment successful! **₹{result['amount']:.2f}** has been paid for Order #{result['order_id']} via Visa card. Transaction ID: `{result['payment_id']}`."
            else:
                reply = result.get("message", "Payment processing encountered an issue.")
            return {
                "reply": reply,
                "tool_called": "pay_order",
                "tool_output": result,
                "data": {"payment": result}
            }

        # 4. RECOMMENDATIONS INTENT
        # Examples: "Recommend laptop bags", "What should I buy?", "Show recommendations", "Recommend keyboards"
        if any(k in msg_lower for k in ["recommend", "suggestion", "suggest", "what should i buy", "catalog", "browse"]):
            result = tool_recommend_products(db, user_id=user_id, query_hint=msg_lower)
            recs_text = "\n".join([f"• **{p['name']}** - ₹{p['price']:.2f} ({p['description']})" for p in result['recommendations']])
            reply = f"Here are top recommendations tailored for you based on your shopping history:\n\n{recs_text}\n\nJust tell me: *'Order a {result['recommendations'][0]['name']}'* to buy right away!"
            return {
                "reply": reply,
                "tool_called": "recommend_products",
                "tool_output": result,
                "data": {"recommendations": result['recommendations']}
            }

        # 5. VIEW ORDERS INTENT
        # Examples: "Show my orders", "List my orders", "Where is my order?", "View orders"
        if any(k in msg_lower for k in ["my order", "orders", "history", "purchases", "view order"]):
            result = tool_get_orders(db, user_id=user_id)
            if result['count'] == 0:
                reply = "You don't have any orders yet. You can order products like Keyboard, Mouse, or Laptop Stand anytime!"
            else:
                orders_list = "\n".join([f"• **Order #{o['id']}**: {o['quantity']}x {o['product']} - ₹{o['amount']:.2f} | Status: **{o['status']}**" for o in result['orders']])
                reply = f"Here are your recent orders:\n\n{orders_list}"
            return {
                "reply": reply,
                "tool_called": "get_orders",
                "tool_output": result,
                "data": {"orders": result['orders']}
            }

        # 6. GREETING / GENERAL ASSISTANT RESPONSE
        reply = (
            f"Hello {user_name}! 👋 I'm **ShopGenie**, your AI conversational shopping assistant.\n\n"
            f"You can speak or type to me naturally! For example:\n"
            f"• *'I want another keyboard'* (Creates an order)\n"
            f"• *'Pay for my latest order'* (Processes payment)\n"
            f"• *'Packaging was poor for order 101'* (Submits feedback & analyzes sentiment)\n"
            f"• *'Recommend laptop bags'* (Provides smart recommendations)"
        )
        return {
            "reply": reply,
            "tool_called": None,
            "tool_output": None,
            "data": None
        }

    def _extract_product_and_qty(self, text: str):
        qty = 1
        # Extract quantity number if present
        qty_match = re.search(r'\b(\d+)\b', text)
        if qty_match:
            qty = int(qty_match.group(1))

        # Extract product name
        known_products = ["keyboard", "mouse", "laptop stand", "laptop bag", "headphones", "usb-c hub", "desk mat", "monitor", "charger"]
        for p in known_products:
            if p in text:
                return p, qty

        # Regex heuristic after verbs
        match = re.search(r'(?:want|order|buy|need|add|another)\s+(?:a\s+|an\s+|the\s+|another\s+|\d+\s+)?([a-zA-Z\s]+)', text)
        if match:
            prod_candidate = match.group(1).strip()
            # clean trailing words
            prod_candidate = re.sub(r'\b(please|now|for me|today|thanks|thank you)\b', '', prod_candidate).strip()
            if prod_candidate:
                return prod_candidate, qty

        return "Keyboard", qty

    def _extract_order_id(self, text: str) -> Optional[int]:
        match = re.search(r'#?(\d{3,5})', text)
        if match:
            return int(match.group(1))
        return None

agent = ShopGenieAgent()
