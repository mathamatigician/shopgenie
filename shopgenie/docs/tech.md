# Technical Documentation - ShopGenie 🧞‍♂️

## 1. Technology Stack

### Backend Stack
- **Framework**: FastAPI (Python 3.12)
- **ASGI Server**: Uvicorn
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: PyJWT (HS256 signature token validation)
- **AI Engine**: ShopGenie Agent (Google Gemini API / NLP Intent Engine)
- **Data Validation**: Pydantic v2

### Frontend Stack
- **Framework**: Vue 3 (Composition API `<script setup>`)
- **Build Tool**: Vite 6
- **Routing**: Vue Router 4 (with route auth guards)
- **State Management**: Reactive Auth Store
- **HTTP Client**: Axios with request authorization interceptors
- **Styling**: Custom Glassmorphism CSS Design System
- **Accessibility**: Web Speech API (SpeechRecognition & SpeechSynthesis)

---

## 2. System Architecture

ShopGenie operates as a decoupled client-server architecture connected over REST and JSON payload APIs.

```
Client (Vue 3 SPA)  <--->  REST API (FastAPI)  <--->  ShopGenie Agent  <--->  SQLite DB
```

### Data Flow for Conversational Shopping:
1. User types or speaks a phrase (e.g. *"Pay for my latest order"*).
2. Frontend sends payload `POST /chat` with message and JWT auth token.
3. Backend extracts current user context from JWT payload.
4. `ShopGenieAgent` parses intent and invokes the matching tool function in `ai/tools.py`.
5. The tool function updates SQLite database via SQLAlchemy session.
6. `ShopGenieAgent` returns structured response containing `reply`, `tool_called`, `tool_output`, and `data`.
7. Frontend renders response bubble, executes voice synthesis if enabled, and updates orders state.

---

## 3. Database Schema & Models

```python
# User Model
class User(Base):
    id: int (PK)
    name: str
    email: str (Unique)
    password: str

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

# Product Catalog Model
class Product(Base):
    id: int (PK)
    name: str
    price: float
    category: str
    description: str
    image: str
```

---

## 4. API Endpoints Specification

### Auth Endpoint
`POST /login`
- **Request Body**: `{"email": "john@test.com", "password": "123456"}`
- **Response**: `{"access_token": "...", "token_type": "bearer", "user": {...}}`

### Orders Endpoints
`GET /orders`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Array of order objects.

`POST /orders`
- **Request Body**: `{"product": "Keyboard", "quantity": 1, "amount": 1999.0}`
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
- **Request Body**: `{"message": "I want another keyboard"}`
- **Response**:
```json
{
  "reply": "I've placed a new order for 1x Keyboard (Order #105) amounting to ₹1999.00.",
  "tool_called": "create_order",
  "tool_output": {"order_id": 105, "status": "Pending", "amount": 1999.0},
  "data": {"order": {...}}
}
```
