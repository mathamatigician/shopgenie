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
    tool_get_orders,
    tool_search_products,
    tool_list_sorted_products,
    tool_get_filtered_orders
)

# In-memory dictionary tracking draft/pending user order selections
draft_orders: Dict[int, Dict[str, Any]] = {}

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

        # 1. COMMAND: LIST AVAILABLE ITEMS WITH SORTING
        # Examples: "List available items for Amul mango ice-creams sorted by price", "List Amul mango ice-creams sorted by price"
        if any(k in msg_lower for k in ["list available", "list items", "sort", "sorted by price", "sorted by"]):
            sort_by = "price_asc"
            if "desc" in msg_lower or "high to low" in msg_lower or "expensive" in msg_lower:
                sort_by = "price_desc"

            # Clean search query terms
            clean_query = re.sub(r'\b(list|available|items|item|for|type|eg|example|sort|sorted|by|price|ascending|descending|low|high|to)\b', ' ', msg_lower, flags=re.IGNORECASE)
            clean_query = re.sub(r'\s+', ' ', clean_query).strip()

            matching_items = tool_list_sorted_products(db, query=clean_query, sort_by=sort_by)

            if matching_items:
                items_text = "\n".join([f"• **{item['name']}** {item['image'] or '📦'} - **₹{item['price']:.2f}** ({item['description']})" for item in matching_items])
                sort_label = "Low to High" if sort_by == "price_asc" else "High to Low"
                reply = (
                    f"Here are the available items matching *'{clean_query or 'all products'}'* (Sorted by Price: **{sort_label}**):\n\n"
                    f"{items_text}\n\n"
                    f"To order any item, just say: *'Order 2 {matching_items[0]['name']}'*"
                )
            else:
                reply = f"No catalog items found matching '{clean_query}'."

            return {
                "reply": reply,
                "tool_called": "list_sorted_products",
                "tool_output": {"query": clean_query, "items": matching_items},
                "data": {"recommendations": matching_items}
            }

        # 2. COMMAND: LIST PAST / LAST ORDERED ITEMS BY CATEGORY/PRODUCT
        # Examples: "List past orders having icecreams", "List last icecreams items ordered", "Show past orders with keyboards"
        if (any(k in msg_lower for k in ["past", "last", "previous", "recent", "history", "purchased"]) and any(k in msg_lower for k in ["order", "orders", "ordered", "items", "item", "having", "with"])) or "having icecreams" in msg_lower or "last icecreams" in msg_lower:
            # Clean product filter term
            clean_filter = re.sub(r'\b(list|show|last|past|previous|recent|having|with|items|item|ordered|orders|order|purchased|my|history)\b', ' ', msg_lower, flags=re.IGNORECASE)
            clean_filter = re.sub(r'\s+', ' ', clean_filter).strip()

            filtered_orders = tool_get_filtered_orders(db, user_id=user_id, filter_term=clean_filter or "all")

            if filtered_orders:
                orders_text = "\n".join([f"• **Order #{o['id']}**: {o['quantity']}x **{o['product']}** - ₹{o['amount']:.2f} | Status: **{o['status']}** ({o['date']})" for o in filtered_orders])
                reply = f"Here are your past orders matching *'{clean_filter or 'all'}'*:\n\n{orders_text}"
            else:
                reply = f"No past orders found matching '{clean_filter}'."

            return {
                "reply": reply,
                "tool_called": "get_filtered_orders",
                "tool_output": {"filter": clean_filter, "orders": filtered_orders},
                "data": {"orders": filtered_orders}
            }

        # 3. FEEDBACK INTENT
        if any(k in msg_lower for k in ["quality", "packaging", "package", "broken", "crushed", "bad", "poor", "terrible", "feedback", "horrible", "damaged", "disappointed"]):
            order_id = self._extract_order_id(msg_lower)
            result = tool_submit_feedback(db, user_id=user_id, message=user_message, order_id=order_id)
            reply = f"*(Feedback Analyzed)* Sentiment: **{result['sentiment']}** | Category: **{result['category']}** | Urgency: **{result['urgency']}**\n\n{result['reply']}"
            return {
                "reply": reply,
                "tool_called": "submit_feedback",
                "tool_output": result,
                "data": {"feedback": result}
            }

        # 4. CONFIRMATION OF DRAFT ORDER INTENT
        if user_id in draft_orders and any(k in msg_lower for k in ["yes", "confirm", "proceed", "pay", "sure", "ok", "okay", "place order", "do it"]):
            draft = draft_orders.pop(user_id)
            order_result = tool_create_order(db, user_id=user_id, product=draft["product"], quantity=draft["quantity"])
            pay_result = tool_pay_order(db, user_id=user_id, order_id=order_result["order_id"])

            reply = (
                f"Order **#{order_result['order_id']}** for **{draft['quantity']}x {order_result['product']}** created successfully!\n\n"
                f"💳 **Payment Successful!** ₹{pay_result['amount']:.2f} paid via Visa (Transaction ID: `{pay_result['payment_id']}`)."
            )

            return {
                "reply": reply,
                "tool_called": "pay_order",
                "tool_output": {"order": order_result, "payment": pay_result},
                "data": {"order": order_result, "payment": pay_result}
            }

        # 5. PRODUCT SEARCH / SELECTION & ORDER DRAFT INTENT
        if any(k in msg_lower for k in ["order", "buy", "purchase", "want", "need", "add", "icecream", "keyboard", "mouse"]):
            query_product, qty = self._extract_product_and_qty(msg_lower)
            matching_products = tool_search_products(db, query=query_product)

            if matching_products:
                selected_prod = matching_products[0]
                unit_price = selected_prod["price"]
                total_cost = unit_price * qty

                draft_orders[user_id] = {
                    "product": selected_prod["name"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "total_cost": total_cost
                }

                options_text = ""
                if len(matching_products) > 1:
                    options_text = "\n\n**Other available variants:**\n" + "\n".join([f"• **{p['name']}** - ₹{p['price']:.2f} ({p['description']})" for p in matching_products[1:3]])

                reply = (
                    f"I found **{selected_prod['name']}** in stock! {selected_prod['image'] or '🍦'}\n\n"
                    f"📦 **Item**: {selected_prod['name']}\n"
                    f"🔢 **Quantity**: {qty}\n"
                    f"💵 **Price**: ₹{unit_price:.2f} each\n"
                    f"💰 **Total Amount**: **₹{total_cost:.2f}**"
                    f"{options_text}\n\n"
                    f"Would you like me to confirm this order and process the payment of **₹{total_cost:.2f}** now? *(Reply 'Yes' or 'Confirm' to complete)*"
                )

                return {
                    "reply": reply,
                    "tool_called": "search_products",
                    "tool_output": {"matches": matching_products, "draft": draft_orders[user_id]},
                    "data": {"recommendations": matching_products}
                }
            else:
                total_cost = 999.0 * qty
                draft_orders[user_id] = {
                    "product": query_product.title(),
                    "quantity": qty,
                    "unit_price": 999.0,
                    "total_cost": total_cost
                }
                reply = (
                    f"I couldn't find an exact catalog match for '{query_product}', but I can custom order **{qty}x {query_product.title()}** for an estimated total of **₹{total_cost:.2f}**.\n\n"
                    f"Would you like to confirm this order and proceed with payment?"
                )
                return {
                    "reply": reply,
                    "tool_called": "search_products",
                    "tool_output": None,
                    "data": None
                }

        # 6. PAYMENT INTENT
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

        # 7. RECOMMENDATIONS INTENT
        if any(k in msg_lower for k in ["recommend", "suggestion", "suggest", "what should i buy", "catalog", "browse"]):
            result = tool_recommend_products(db, user_id=user_id, query_hint=msg_lower)
            recs_text = "\n".join([f"• **{p['name']}** - ₹{p['price']:.2f} ({p['description']})" for p in result['recommendations']])
            reply = f"Here are top recommendations tailored for you based on your shopping history:\n\n{recs_text}\n\nJust tell me: *'Order a {result['recommendations'][0]['name']}'* to inspect & buy right away!"
            return {
                "reply": reply,
                "tool_called": "recommend_products",
                "tool_output": result,
                "data": {"recommendations": result['recommendations']}
            }

        # 8. VIEW ALL ORDERS INTENT
        if any(k in msg_lower for k in ["my order", "orders", "history", "purchases", "view order"]):
            result = tool_get_orders(db, user_id=user_id)
            if result['count'] == 0:
                reply = "You don't have any orders yet. You can order products like Keyboard, Mouse, or Amul Ice Cream anytime!"
            else:
                orders_list = "\n".join([f"• **Order #{o['id']}**: {o['quantity']}x {o['product']} - ₹{o['amount']:.2f} | Status: **{o['status']}**" for o in result['orders']])
                reply = f"Here are your recent orders:\n\n{orders_list}"
            return {
                "reply": reply,
                "tool_called": "get_orders",
                "tool_output": result,
                "data": {"orders": result['orders']}
            }

        # 9. GREETING / GENERAL ASSISTANT RESPONSE
        reply = (
            f"Hello {user_name}! 👋 I'm **ShopGenie**, your AI conversational shopping assistant.\n\n"
            f"You can speak or type to me naturally! For example:\n"
            f"• *'List Amul mango ice-creams sorted by price'*\n"
            f"• *'List past orders having icecreams'*\n"
            f"• *'Create a new order for 2 icecereams 100 ml each. Amul brand only.'*\n"
            f"• *'Pay for my latest order'*"
        )
        return {
            "reply": reply,
            "tool_called": None,
            "tool_output": None,
            "data": None
        }

    def _extract_product_and_qty(self, text: str):
        qty = 1
        qty_match = re.search(r'\b(\d+)\b', text)
        if qty_match:
            qty = int(qty_match.group(1))

        known_products = [
            "amul alphonso mango ice cream", "amul mango duet ice cream", "amul mango kulfi",
            "amul vanilla ice cream", "amul chocolate ice cream", "amul butterscotch ice cream", 
            "amul ice cream", "mango ice cream", "icecream", "ice cream", "amul", 
            "keyboard", "mouse", "laptop stand", "laptop bag", 
            "headphones", "usb-c hub", "desk mat"
        ]
        for p in known_products:
            if p in text:
                return p, qty

        cleaned = re.sub(r'\b(create|a|new|order|for|each|brand|only|ml|100ml|100|please|now|want|buy|need|add)\b', ' ', text, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        if cleaned and len(cleaned) > 2:
            return cleaned, qty

        return "amul ice cream", qty

    def _extract_order_id(self, text: str) -> Optional[int]:
        match = re.search(r'#?(\d{3,5})', text)
        if match:
            return int(match.group(1))
        return None

agent = ShopGenieAgent()
