# AI Use Cases & Tool Calling Documentation - ShopGenie 🧞‍♂️

## Overview
ShopGenie provides a natural language interface that replaces standard GUI screens (search, checkout, payment forms, feedback forms) with automated **AI Tool Calling**.

---

## 1. AI Use Case 1: Order Creation

### User Scenario
The user wants to order a product without browsing catalog pages.

- **User Input**: `"I want another keyboard"` / `"Order another mouse"` / `"Buy 2 laptop stands"`
- **Extracted Intent**: Order Creation
- **Tool Invoked**: `tool_create_order(db, user_id, product, quantity)`
- **Tool Signature**:
```python
create_order(
    user_id: int,
    product: str,
    quantity: int = 1
)
```
- **Tool Output**:
```json
{
  "order_id": 105,
  "product": "Keyboard",
  "quantity": 1,
  "amount": 1999.0,
  "status": "Pending",
  "message": "Order #105 for 1x 'Keyboard' created successfully! Total: ₹1999.00. Status: Pending Payment."
}
```
- **Assistant Response**:
  > "I've placed a new order for **1x Keyboard** (Order #105) amounting to **₹1999.00**. Status is currently **Pending**. Would you like to pay for it now?"

---

## 2. AI Use Case 2: Instant Payment Processing

### User Scenario
The user wants to pay for an order using their saved card or payment method without navigating to a multi-step checkout screen.

- **User Input**: `"Pay for my latest order"` / `"Pay order 102"` / `"Pay using saved card"`
- **Extracted Intent**: Payment Processing
- **Tool Invoked**: `tool_pay_order(db, user_id, order_id=None)`
- **Tool Signature**:
```python
pay_order(
    user_id: int,
    order_id: Optional[int] = None
)
```
- **Tool Output**:
```json
{
  "order_id": 105,
  "payment_id": "P105",
  "amount": 1999.0,
  "status": "Paid",
  "message": "Payment of ₹1999.00 completed successfully for Order #105 using saved card (Visa)."
}
```
- **Assistant Response**:
  > "Payment successful! **₹1999.00** has been paid for Order #105 via Visa card. Transaction ID: `P105`."

---

## 3. AI Use Case 3: Feedback & Sentiment Analysis

### User Scenario
Instead of filling out star ratings and multi-page surveys, the user describes their product/delivery experience in natural text.

- **User Input**: `"Packaging was poor for order 101. The box arrived crushed."`
- **Extracted Intent**: Feedback Submission & Sentiment Analysis
- **Tool Invoked**: `tool_submit_feedback(db, user_id, message, order_id=None)`
- **NLP Analysis Output**:
  - **Sentiment**: `Negative`
  - **Category**: `Packaging`
  - **Urgency**: `High`
  - **Keywords**: `packaging, crushed, poor`
- **Tool Output**:
```json
{
  "feedback_id": 2,
  "order_id": 101,
  "sentiment": "Negative",
  "category": "Packaging",
  "urgency": "High",
  "keywords": "packaging, crushed, poor",
  "reply": "We're deeply sorry to hear about your experience regarding the packaging..."
}
```
- **Assistant Response**:
  > "*(Feedback Analyzed)* Sentiment: **Negative** | Category: **Packaging** | Urgency: **High**\n\nWe're deeply sorry to hear about your experience regarding the packaging. We've flagged this with High Priority to ensure our team addresses it immediately."

---

## 4. AI Use Case 4: Smart Product Recommendations

### User Scenario
The user asks for product suggestions based on their purchase history.

- **User Input**: `"Recommend laptop bags"` / `"What should I buy?"`
- **Extracted Intent**: Product Recommendation
- **Tool Invoked**: `tool_recommend_products(db, user_id, query_hint="laptop bags")`
- **Tool Output**:
```json
{
  "user_id": 1,
  "recommendations": [
    {
      "id": 4,
      "name": "Laptop Bag",
      "price": 1299.0,
      "category": "Accessories",
      "description": "Water-resistant stylish laptop backpack with padded compartment.",
      "image": "🎒"
    }
  ]
}
```
- **Assistant Response**:
  > "Here are top recommendations tailored for you based on your shopping history:\n\n• **Laptop Bag** - ₹1299.00 (Water-resistant stylish laptop backpack)\n\nJust tell me: *'Order a Laptop Bag'* to buy right away!"
