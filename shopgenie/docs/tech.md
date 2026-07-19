# Technical Documentation - ShopGenie 🧞‍♂️ (Version 1.2)

## 1. Technology Stack

### Backend Stack
- **Framework**: FastAPI (Python 3.12)
- **ASGI Server**: Uvicorn (StatReload enabled)
- **Database**: SQLite (`shopgenie.db`) with SQLAlchemy ORM
- **Seeding Pipeline**: Dynamic CSV parser (`inventory.csv` + `additional_inventory.csv`)
- **Authentication**: PyJWT (HS256 signature token validation)
- **AI Engine**: ShopGenie Agent (Google Gemini API / Hybrid Rule & Intent Engine)
- **Data Validation**: Pydantic v2

### Frontend Stack
- **Framework**: Vue 3 (Composition API `<script setup>`)
- **Build Tool**: Vite 6
- **Routing**: Vue Router 4 (with route auth guards)
- **State Management**: Reactive Auth Store & Cart State
- **HTTP Client**: Axios with request authorization interceptors
- **Styling**: Custom Glassmorphic CSS Design System
- **Accessibility**: Web Speech API (SpeechRecognition & SpeechSynthesis)

---

## 2. System Architecture & Component Interaction

ShopGenie operates as a decoupled client-server architecture connected over REST and JSON payload APIs.

```
Client (Vue 3 SPA)  <--->  REST API (FastAPI)  <--->  ShopGenie Agent  <--->  SQLite DB
```

### Data Flow for Conversational Shopping:
1. User types or speaks a phrase (e.g. *"Create an order for 1. Amul 500g ice-cream pack 1 Qty 2. Balaji Potato Chips 20 Rs pack 5 Qty."*).
2. Frontend sends payload `POST /chat` with message and JWT auth token header.
3. Backend extracts current user context from JWT payload.
4. `ShopGenieAgent` parses multi-item requests, validates inventory per item against SQLite DB, builds cart draft, and resolves out-of-stock items with alternate suggestions.
5. The tool function updates SQLite database via SQLAlchemy session upon confirmation.
6. `ShopGenieAgent` returns structured response containing `reply`, `tool_called`, `tool_output`, and `data`.
7. Frontend renders response bubble, executes voice synthesis if enabled, and updates orders/cart UI state.

---

## 3. Database Schema & ORM Models

```python
# User Model
class User(Base):
    id: int (PK)
    name: str
    email: str (Unique)
    password: str

# Product Catalog Model (Populated from CSVs)
class Product(Base):
    id: int (PK)
    sku: str (SKU001, SKU031...)
    name: str
    price: float
    category: str
    brand: str
    stock: int
    description: str
    image: str

# Order Model
class Order(Base):
    id: int (PK)
    user_id: int (FK -> User.id)
    product: str
    quantity: int
    amount: float
    status: str ("Pending", "Paid", "Delivered")
    date: datetime

# Payment Model
class Payment(Base):
    id: str (PK, e.g. "P101")
    order_id: int (FK -> Order.id)
    method: str ("Visa", "Mastercard", "UPI")
    status: str ("Paid", "Pending", "Refunded")
    amount: float
    date: datetime

# Feedback Model
class Feedback(Base):
    id: int (PK)
    order_id: int (FK -> Order.id)
    user_id: int (FK -> User.id)
    message: str
    sentiment: str ("Positive", "Negative", "Neutral")
    category: str ("Packaging", "Quality", "Delivery", "Customer Service")
    urgency: str ("Low", "Medium", "High")
    keywords: str
    created_at: datetime
```

---

## 4. Seeding Pipeline & CSV Schema

Database seeding is powered by [seed.py](file:///mnt/c/Users/Harshit/Downloads/Hackathons/Amadeus_final/shopgenie/database/seed.py), which reads from two CSV files:
- [inventory.csv](file:///mnt/c/Users/Harshit/Downloads/Hackathons/Amadeus_final/shopgenie/database/inventory.csv): 30 base grocery and snack items (`SKU001` - `SKU030`)
- [additional_inventory.csv](file:///mnt/c/Users/Harshit/Downloads/Hackathons/Amadeus_final/shopgenie/database/additional_inventory.csv): 19 additional ice creams, dairy, snacks, and electronics items (`SKU031` - `SKU049`)

### CSV Field Structure:
`SKU, Category, ItemName, QuantityInStock, UnitPriceINR, Brand`

---

## 5. AI Tool Calling Engine & User Query Translation Specifications

> For detailed specifications on how user queries are translated, parsed, and routed for all use cases, see [query_translation.md](file:///mnt/c/Users/Harshit/Downloads/Hackathons/Amadeus_final/shopgenie/docs/query_translation.md).

| Tool Function | Intent / Trigger | Description |
|---|---|---|
| `tool_create_order` | `"Order X"`, `"Confirm"` | Creates new order in DB and decrements item stock. |
| `tool_pay_order` | `"Pay for order"` | Processes payment via Visa/UPI & updates status to Paid. |
| `tool_submit_feedback` | `"Packaging was poor..."` | Extracts sentiment, category, urgency, & keywords. |
| `tool_recommend_products` | `"Recommend bags"` | Generates recommendations based on purchase history. |
| `tool_search_products` | `"Search X"` | Searches items across SKU, Brand, Name, & Category. |
| `tool_list_sorted_products` | `"List X sorted by price"` | Returns items sorted by price (`price_asc` / `price_desc`). |
| `tool_get_filtered_orders` | `"List past orders having X"` | Filters user's order history by product type/category. |
| `view_cart` | `"show cart option"` | Displays active draft cart items, subtotals, and total. |
| `update_cart_quantity` | `"Update quantity of X to N"` | Modifies quantity of item in active draft cart. |
| `clear_cart` | `"clear cart"` | Clears current user's active draft cart. |

---

## 6. API Endpoints Specification

### Auth Endpoint
`POST /login`
- **Request Body**: `{"email": "john@test.com", "password": "123456"}`
- **Response**: `{"access_token": "...", "token_type": "bearer", "user": {...}}`

### Orders Endpoints
`GET /orders`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Array of user order objects.

`POST /orders`
- **Request Body**: `{"product": "Amul Vanilla Ice Cream 100ml", "quantity": 2, "amount": 100.0}`
- **Response**: Order object.

### Payment Endpoints
`POST /payment`
- **Request Body**: `{"order_id": 102, "method": "Visa"}`
- **Response**: `{"status": "Success", "payment_id": "P102", "amount": 899.0}`

### Feedback Endpoints
`POST /feedback`
- **Request Body**: `{"message": "Packaging was poor for order 101", "order_id": 101}`
- **Response**: `{"feedback_id": 1, "sentiment": "Negative", "category": "Packaging", "urgency": "High", "reply": "..."}`

### Chat Endpoint
`POST /chat`
- **Request Body**: `{"message": "show cart option"}`
- **Response**:
```json
{
  "reply": "🛒 Your Current Shopping Cart:\n\n• Amul Vanilla Ice Cream 100ml 🍦 — Qty: 2 | Price: ₹50.00 each | Subtotal: ₹100.00\n\n💰 Total Cart Amount: ₹100.00",
  "tool_called": "view_cart",
  "tool_output": {"cart": [...], "total_amount": 100.0},
  "data": {"cart": [...]}
}
```
