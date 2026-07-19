# ShopGenie 🧞‍♂️
> **AI-First Conversational E-Commerce Platform**

ShopGenie eliminates traditional e-commerce friction (multi-page navigation, complex checkout forms, search filters) by empowering users to search, order, pay, get recommendations, and submit feedback entirely through natural language conversation.

---

## 🌟 Key Features

1. **AI-First Conversational Shopping**
   - Place orders, pay bills, and submit feedback entirely via text or voice.
   - Real-time AI Tool Calling execution with visual status indicators.

2. **Automated Tool Calling**
   - `create_order(user_id, product, quantity)`: Instantly creates new orders.
   - `pay_order(order_id, method)`: Processes payments for pending orders.
   - `submit_feedback(order_id, message)`: Extracts sentiment, category, urgency, and keywords.
   - `recommend_products(user_id)`: Generates personalized product suggestions.

3. **Accessibility & Multi-modal Input**
   - Designed for elderly, mobile, and visually impaired customers.
   - Built-in Speech-to-Text (Voice input) and Text-to-Speech output.

4. **JWT Authentication & Seeded Accounts**
   - Instant 1-click test login for standard PRD profiles (`John`, `Alice`, `Bob`).

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
cd shopgenie
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy pyjwt pydantic python-multipart google-genai

# Seed Database with initial Users, Orders, Payments, Feedbacks
python database/seed.py

# Run FastAPI Backend Server
cd backend
uvicorn app:app --reload --port 8000
```
Backend will run at: `http://localhost:8000` (API Docs at `http://localhost:8000/docs`).

### 3. Frontend Setup
```bash
cd shopgenie/frontend
npm install
npm run dev
```
Frontend will run at: `http://localhost:3000`.

---

## 🧪 Test Accounts & Credentials

| User | Email | Password | Pre-seeded Orders |
|---|---|---|---|
| **John** | `john@test.com` | `123456` | Order #101 (Keyboard - Delivered), #102 (Mouse - Pending), #103 (Laptop Stand - Paid) |
| **Alice** | `alice@test.com` | `password` | Order #104 (Headphones - Delivered) |
| **Bob** | `bob@test.com` | `abc123` | New User |

---

## 🗣️ Sample Conversational Prompts to Try

1. **Order Creation**: `"I want another keyboard"`
2. **Payment**: `"Pay for my latest order"` or `"Pay order 102"`
3. **Feedback & Sentiment Analysis**: `"Packaging was poor for order 101. The box arrived crushed."`
4. **Recommendations**: `"Recommend laptop bags"`
5. **View History**: `"Show my orders"`

---

## 📐 Project Architecture

```
shopgenie/
├── backend/
│   ├── app.py          # FastAPI Main Entry
│   ├── auth.py         # JWT Login & Authentication
│   ├── chat.py         # Chat Endpoint & Controller
│   ├── orders.py       # Orders Controller
│   ├── payments.py     # Payments Controller
│   ├── feedback.py     # Feedback Controller
│   ├── database.py     # SQLite SQLAlchemy DB Setup
│   ├── models.py       # ORM Data Models
│   └── ai/
│       ├── agent.py    # ShopGenie AI Agent & Intent Router
│       └── tools.py    # AI Tool Implementation Functions
├── frontend/
│   ├── src/
│   │   ├── views/      # Login, Dashboard, Orders, Payments, Chat
│   │   ├── components/ # Navbar, ChatWindow
│   │   ├── store/      # Reactive Auth Store
│   │   ├── router/     # Vue Router Guards
│   │   └── services/   # Axios API Service Layer
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── query_translation.md  # Detailed User Query Translation Specifications
│   ├── tech.md               # Technical Architecture Documentation
│   ├── PRD.md                # Product Requirements Document
│   └── usecases.md           # Business & Demo Use Cases
├── database/
│   └── seed.py               # DB Seeder Script
└── README.md
```
