import os
import re
import json
from typing import Dict, Any, Optional, List
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
from models import Product

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

        # 1. COMMAND: UPDATE ITEM QUANTITY IN CART
        # Examples: "Update quantity of Amul Vanilla Ice Cream to 5", "Change qty of keyboard to 3", "Update quantity to 4"
        if any(k in msg_lower for k in ["update quantity", "change quantity", "set quantity", "modify quantity", "update qty", "change qty", "set qty"]):
            user_draft = draft_orders.get(user_id)
            if not user_draft or not user_draft.get("items"):
                reply = "🛒 **Your cart is currently empty.** Add an item first by saying e.g. *'Order 2 Amul Vanilla Ice Cream'*!"
                return {
                    "reply": reply,
                    "tool_called": "update_cart_quantity",
                    "tool_output": {"status": "failed", "reason": "empty_cart"},
                    "data": None
                }

            # Extract target quantity number
            qty_match = re.search(r'\bto\s+(\d+)\b', msg_lower)
            if not qty_match:
                qty_match = re.search(r'\b(\d+)\b', msg_lower)

            if not qty_match:
                reply = "Please specify the target quantity (e.g., *'Update quantity of Amul Vanilla Ice Cream to 5'*)."
                return {
                    "reply": reply,
                    "tool_called": "update_cart_quantity",
                    "tool_output": {"status": "failed", "reason": "missing_quantity"},
                    "data": None
                }

            new_qty = max(1, int(qty_match.group(1)))
            cart_items = user_draft["items"]

            # Match product in cart or default to last item
            target_item = cart_items[-1]  # Default to last added item
            clean_item_query = re.sub(r'\b(update|change|set|modify|quantity|qty|of|to|\d+)\b', ' ', msg_lower, flags=re.IGNORECASE).strip()

            if clean_item_query:
                for item in cart_items:
                    if clean_item_query in item["product"].lower() or any(term in item["product"].lower() for term in clean_item_query.split()):
                        target_item = item
                        break

            old_qty = target_item["quantity"]
            target_item["quantity"] = new_qty
            target_item["total_cost"] = target_item["unit_price"] * new_qty

            total_amount = sum(i["total_cost"] for i in cart_items)
            user_draft["total_cart_amount"] = total_amount

            reply = (
                f"✏️ **Cart Quantity Updated Successfully!**\n\n"
                f"• **{target_item['product']}** {target_item.get('image', '📦')} — Quantity updated: **{old_qty} ➔ {new_qty}** | Price: ₹{target_item['unit_price']:.2f} each | Item Subtotal: **₹{target_item['total_cost']:.2f}**\n\n"
                f"💰 **New Total Cart Amount**: **₹{total_amount:.2f}**\n\n"
                f"Would you like to confirm and process payment of **₹{total_amount:.2f}** now? *(Reply 'Yes' or 'Confirm' to complete)*"
            )

            return {
                "reply": reply,
                "tool_called": "update_cart_quantity",
                "tool_output": {"updated_item": target_item, "new_qty": new_qty, "total_amount": total_amount},
                "data": {"cart": cart_items}
            }

        # 2. COMMAND: SHOW CART / VIEW CART
        if any(k in msg_lower for k in ["show cart", "view cart", "my cart", "cart option", "cart options", "current cart", "check cart"]) or msg_lower == "cart":
            user_draft = draft_orders.get(user_id)
            if not user_draft or not user_draft.get("items"):
                reply = (
                    f"🛒 **Your Shopping Cart is Currently Empty**\n\n"
                    f"You can add products to your cart anytime by saying:\n"
                    f"• *'Order 2 Amul Vanilla Ice Cream'*\n"
                    f"• *'Order 5 Lays Potato Chips'*\n"
                    f"• *'Add a mechanical keyboard'*"
                )
                return {
                    "reply": reply,
                    "tool_called": "view_cart",
                    "tool_output": {"status": "empty"},
                    "data": {"cart": []}
                }
            else:
                cart_items = user_draft["items"]
                total_amount = user_draft.get("total_cart_amount", sum(item["total_cost"] for item in cart_items))

                items_text = "\n".join([f"• **{item['product']}** {item.get('image', '📦')} — Qty: **{item['quantity']}** | Price: ₹{item['unit_price']:.2f} each | Subtotal: **₹{item['total_cost']:.2f}**" for item in cart_items])

                reply = (
                    f"🛒 **Your Current Shopping Cart:**\n\n"
                    f"{items_text}\n\n"
                    f"💰 **Total Cart Amount**: **₹{total_amount:.2f}**\n\n"
                    f"Would you like to confirm this order and process payment of **₹{total_amount:.2f}** now? *(Reply 'Yes' or 'Confirm' to complete)*"
                )
                return {
                    "reply": reply,
                    "tool_called": "view_cart",
                    "tool_output": {"cart": cart_items, "total_amount": total_amount},
                    "data": {"cart": cart_items}
                }

        # 3. COMMAND: CLEAR CART
        if any(k in msg_lower for k in ["clear cart", "empty cart", "reset cart"]):
            draft_orders.pop(user_id, None)
            reply = "🛒 **Your shopping cart has been cleared.**"
            return {
                "reply": reply,
                "tool_called": "clear_cart",
                "tool_output": {"status": "cleared"},
                "data": None
            }

        # 4. COMMAND: LIST AVAILABLE ITEMS WITH SORTING
        if any(k in msg_lower for k in ["list available", "list items", "sort", "sorted by price", "sorted by"]):
            sort_by = "price_asc"
            if "desc" in msg_lower or "high to low" in msg_lower or "expensive" in msg_lower:
                sort_by = "price_desc"

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

        # 5. COMMAND: LIST PAST / LAST ORDERED ITEMS BY CATEGORY/PRODUCT
        if (any(k in msg_lower for k in ["past", "last", "previous", "recent", "history", "purchased"]) and any(k in msg_lower for k in ["order", "orders", "ordered", "items", "item", "having", "with"])) or "having ice" in msg_lower or "past orders" in msg_lower or "last icecreams" in msg_lower:
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

        # 6. FEEDBACK INTENT
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

        # 7. CONFIRMATION OF DRAFT ORDER INTENT
        if user_id in draft_orders and any(k in msg_lower for k in ["yes", "confirm", "proceed", "pay", "sure", "ok", "okay", "place order", "do it"]):
            draft = draft_orders.pop(user_id)
            items_to_create = draft.get("items", [draft])

            order_results = []
            pay_results = []
            total_paid = 0.0

            for item in items_to_create:
                o_res = tool_create_order(db, user_id=user_id, product=item["product"], quantity=item["quantity"])
                p_res = tool_pay_order(db, user_id=user_id, order_id=o_res["order_id"])
                order_results.append(o_res)
                pay_results.append(p_res)
                total_paid += o_res["amount"]

            created_summary = ", ".join([f"Order #{o['order_id']} ({o['quantity']}x {o['product']})" for o in order_results])
            reply = (
                f"🎉 **Order Placed Successfully!**\n"
                f"📦 **Created Orders**: {created_summary}\n\n"
                f"💳 **Payment Successful!** Total **₹{total_paid:.2f}** paid via Visa."
            )

            return {
                "reply": reply,
                "tool_called": "pay_order",
                "tool_output": {"orders": order_results, "payments": pay_results},
                "data": {"orders": order_results, "payments": pay_results}
            }

        # 8. PRODUCT SEARCH, MULTI-ITEM INVENTORY CHECK & ORDER DRAFT INTENT
        if any(k in msg_lower for k in ["order", "buy", "purchase", "want", "need", "add", "icecream", "keyboard", "chips"]) and not any(k in msg_lower for k in ["list", "show", "history", "last", "past", "previous", "view", "update", "change", "set"]):
            parsed_items = self._parse_items_from_message(user_message)
            
            in_stock_items = []
            out_of_stock_reports = []
            total_cart_amount = 0.0

            for req in parsed_items:
                search_query = req["query"]
                requested_qty = req["quantity"]

                matches = tool_search_products(db, query=search_query)

                exact_match = None
                if matches:
                    top_match = matches[0]
                    query_lower = search_query.lower()

                    if ("500g" in query_lower and "500g" not in top_match["name"].lower()) or \
                       ("balaji" in query_lower and "balaji" not in top_match["name"].lower()):
                        exact_match = None
                    else:
                        exact_match = top_match

                if exact_match:
                    unit_price = exact_match["price"]
                    item_total = unit_price * requested_qty
                    total_cart_amount += item_total
                    in_stock_items.append({
                        "product": exact_match["name"],
                        "quantity": requested_qty,
                        "unit_price": unit_price,
                        "total_cost": item_total,
                        "image": exact_match["image"] or "📦"
                    })
                else:
                    alternates = self._find_alternate_options(db, search_query)
                    out_of_stock_reports.append({
                        "requested_item": req["raw_text"],
                        "quantity": requested_qty,
                        "query": search_query,
                        "alternates": alternates
                    })

            reply_parts = []

            if in_stock_items:
                reply_parts.append("✅ **In Stock & Added to Cart Draft:**")
                for item in in_stock_items:
                    reply_parts.append(f"• **{item['product']}** {item['image']} - Qty: {item['quantity']} | Price: ₹{item['unit_price']:.2f} each | Total: **₹{item['total_cost']:.2f}**")

            if out_of_stock_reports:
                reply_parts.append("\n❌ **Out of Stock / Not Matched Items & Alternate Options:**")
                for oos in out_of_stock_reports:
                    reply_parts.append(f"\n**Item: \"{oos['requested_item']}\" (Qty: {oos['quantity']})**")
                    reply_parts.append("• Status: ❌ **Currently Out of Stock**")
                    if oos["alternates"]:
                        reply_parts.append("• 💡 **Available Alternate Options in Store:**")
                        for alt in oos["alternates"][:3]:
                            alt_total = alt['price'] * oos['quantity']
                            reply_parts.append(f"  - **{alt['name']}** {alt['image'] or '📦'} — ₹{alt['price']:.2f} each (Total for {oos['quantity']}x: **₹{alt_total:.2f}**)")
                    else:
                        reply_parts.append("  - No direct alternate options found in catalog.")

            if in_stock_items:
                existing_cart = draft_orders.get(user_id, {}).get("items", [])
                combined_items = existing_cart + in_stock_items
                total_combined_amount = sum(i["total_cost"] for i in combined_items)

                draft_orders[user_id] = {
                    "items": combined_items,
                    "total_cart_amount": total_combined_amount
                }
                reply_parts.append(f"\n💰 **Available Cart Subtotal**: **₹{total_combined_amount:.2f}**")
                reply_parts.append("\nWould you like to confirm and process payment for the in-stock items, or select one of the alternate options? *(Reply 'Yes' or 'Confirm' to pay available items)*")
            else:
                reply_parts.append("\nWould you like to select one of the alternate options listed above? Reply with your choice like: *'Order 2 Amul Vanilla Ice Cream'* or *'Order 5 Lays Potato Chips'*!")

            full_reply = "\n".join(reply_parts)

            return {
                "reply": full_reply,
                "tool_called": "search_products",
                "tool_output": {"in_stock": in_stock_items, "out_of_stock": out_of_stock_reports},
                "data": {"recommendations": [alt for oos in out_of_stock_reports for alt in oos["alternates"]]}
            }

        # 9. PAYMENT INTENT
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

        # 10. RECOMMENDATIONS INTENT
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

        # 11. VIEW ALL ORDERS INTENT
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

        # 12. GREETING / GENERAL ASSISTANT RESPONSE
        reply = (
            f"Hello {user_name}! 👋 I'm **ShopGenie**, your AI conversational shopping assistant.\n\n"
            f"You can speak or type to me naturally! For example:\n"
            f"• *'Update quantity of Amul Vanilla Ice Cream to 5'*\n"
            f"• *'show cart option'*\n"
            f"• *'Order 2 Amul Vanilla Ice Cream'*\n"
            f"• *'List Amul mango ice-creams sorted by price'*"
        )
        return {
            "reply": reply,
            "tool_called": None,
            "tool_output": None,
            "data": None
        }

    def _parse_items_from_message(self, text: str) -> List[Dict[str, Any]]:
        numbered_matches = re.findall(r'(?:\d+[\.\)]\s*)([^1-9\.\)]+)', text)
        items = []

        if len(numbered_matches) >= 2:
            for raw_item in numbered_matches:
                clean_text = raw_item.strip()
                qty = 1
                qty_match = re.search(r'(\d+)\s*(?:qty|quantity|pcs|pieces)\b', clean_text, flags=re.IGNORECASE)
                if not qty_match:
                    qty_match = re.search(r'\b(?:qty|quantity)\s*(\d+)\b', clean_text, flags=re.IGNORECASE)
                if qty_match:
                    qty = int(qty_match.group(1))

                clean_query = re.sub(r'\b\d+\s*(?:qty|quantity|pcs|pieces)\b', ' ', clean_text, flags=re.IGNORECASE).strip()
                clean_query = re.sub(r'\b(?:qty|quantity)\s*\d+\b', ' ', clean_query, flags=re.IGNORECASE).strip()

                items.append({
                    "raw_text": clean_text,
                    "quantity": qty,
                    "query": clean_query or clean_text
                })
        else:
            prod, qty = self._extract_product_and_qty(text)
            items.append({
                "raw_text": text,
                "quantity": qty,
                "query": prod
            })

        return items

    def _find_alternate_options(self, db: Session, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        all_prods = db.query(Product).all()
        alternates = []

        if "chips" in query_lower or "potato" in query_lower or "snack" in query_lower or "balaji" in query_lower:
            alternates = [p for p in all_prods if p.category == "Snacks" or "chips" in p.name.lower()]
        elif "ice" in query_lower or "cream" in query_lower or "amul" in query_lower:
            alternates = [p for p in all_prods if p.category == "Dairy & Frozen" or "ice cream" in p.name.lower()]

        if not alternates:
            alternates = all_prods[:3]

        return [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "category": p.category,
                "description": p.description,
                "image": p.image
            } for p in alternates
        ]

    def _extract_product_and_qty(self, text: str):
        qty = 1
        qty_match = re.search(r'\b(\d+)\b', text)
        if qty_match:
            qty = int(qty_match.group(1))

        known_products = [
            "amul alphonso mango ice cream", "amul mango duet ice cream", "amul mango kulfi",
            "amul vanilla ice cream", "amul chocolate ice cream", "amul butterscotch ice cream", 
            "amul ice cream", "mango ice cream", "icecream", "ice cream", "amul", 
            "lays classic salted potato chips", "bingo mad angles potato chips", "kurkure masala munch",
            "potato chips", "chips", "keyboard", "mouse", "laptop stand", "laptop bag"
        ]
        for p in known_products:
            if p in text.lower():
                return p, qty

        cleaned = re.sub(r'\b(create|an|a|new|order|for|each|brand|only|ml|100ml|100|please|now|want|buy|need|add)\b', ' ', text, flags=re.IGNORECASE)
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
