# AI Use Cases & Tool Calling Documentation - ShopGenie 🧞‍♂️

## Overview
ShopGenie provides a natural language interface that replaces standard GUI screens (search, checkout, payment forms, feedback forms) with automated **AI Tool Calling**.

---

## 1. AI Use Case 1: Product Listing with Sorting
List catalog items for a specific brand or product type sorted by price (ascending or descending).

- **User Command**: `"List Amul mango ice-creams sorted by price"`
- **Tool Invoked**: `tool_list_sorted_products(db, query="amul mango ice-creams", sort_by="price_asc")`
- **Output**:
  > Here are the available items matching *'amul mango ice-creams'* (Sorted by Price: **Low to High**):
  > • **Amul Mango Kulfi 100ml** 🥭 - **₹40.00**
  > • **Amul Mango Duet Ice Cream 100ml** 🥭 - **₹45.00**
  > • **Amul Alphonso Mango Ice Cream 100ml** 🥭 - **₹65.00**

---

## 2. AI Use Case 2: Past Orders Filtered by Product
View previous orders matching a specific product type or category.

- **User Command**: `"List last icecreams items ordered"`
- **Tool Invoked**: `tool_get_filtered_orders(db, user_id=1, filter_term="icecreams")`
- **Output**:
  > Here are your last ordered items matching *'icecreams'*:
  > • **Order #104**: 2x **Amul Mango Duet Ice Cream 100ml** - ₹90.00 | Status: **Delivered** (2026-07-18 08:15)

---

## 3. AI Use Case 3: Order Search & Draft Confirmation

- **User Command**: `"Create a new order for 2 icecereams 100 ml each. Amul brand only."`
- **AI Response**:
  > I found **Amul Vanilla Ice Cream 100ml** in stock! 🍦
  > 📦 **Item**: Amul Vanilla Ice Cream 100ml
  > 🔢 **Quantity**: 2
  > 💵 **Price**: ₹50.00 each
  > 💰 **Total Amount**: **₹100.00**
  >
  > Would you like me to confirm this order and process the payment of **₹100.00** now?
- **User Confirmation**: `"Yes, confirm and pay"`
- **AI Action**: Creates order and processes payment.

---

## 4. AI Use Case 4: Feedback & Sentiment Analysis

- **User Command**: `"Packaging was poor for order 101. The box arrived crushed."`
- **NLP Analysis Output**: Sentiment: `Negative` | Category: `Packaging` | Urgency: `High`
