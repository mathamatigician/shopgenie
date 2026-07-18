# Product Requirement Document (PRD) - ShopGenie 🧞‍♂️

## 1. Problem Statement
Current e-commerce platforms (Amazon, Flipkart, etc.) require users to navigate across multiple screens and pages:
- Searching products across categories and filters
- Checkout flow & multi-step forms
- Payment page & payment method selections
- Post-purchase feedback and rating forms

This multi-step, screen-heavy process increases user friction, causes cart abandonment, and creates accessibility barriers for elderly and visually impaired users.

---

## 2. Goal
Build an **AI-First Conversational E-Commerce Experience** where customers complete their entire shopping journey—searching items, placing orders, processing payments, getting personalized recommendations, and submitting feedback—**entirely through natural language conversation**.

---

## 3. Target Users
- **Amazon & Flipkart Users**: Seeking zero-click, rapid shopping experiences.
- **Elderly Customers**: Preferring natural speech and simple conversational commands over complex GUI navigation.
- **Mobile Users**: Wanting fast voice/text ordering without multi-tab switching.
- **Visually Impaired Users**: Leveraging screen readers, voice input, and spoken audio responses.

---

## 4. Key Features

### 4.1 Authentication
- **Fake Login**: Email and password login (`john@test.com` / `123456`).
- **JWT Generation**: Returns a signed JSON Web Token for authenticated API calls.
- **Quick Test Fill**: 1-click credential buttons for John, Alice, and Bob.

### 4.2 Orders Page
- Display Order ID, Product Items, Quantity, Amount (₹), Status (*Pending*, *Paid*, *Delivered*), and Date.
- Filter orders by status tabs.
- Quick action buttons to pay pending orders.

### 4.3 Payments Page
- Display payment receipts, method (Visa, Mastercard, UPI), status, amount, and timestamp.
- Banner alert for active pending orders with instant pay option.

### 4.4 AI Chat Window
- Natural language text and voice processing.
- Real-time tool execution badges (e.g. `🤖 Tool Called: create_order`).
- Quick prompt suggestion chips:
  - `"I want another keyboard"`
  - `"Pay for my latest order"`
  - `"Packaging was poor for order 101"`
  - `"Recommend laptop bags"`
- Voice input button (Web Speech API integration for accessibility).
- Text-to-speech auto-read option.

---

## 5. AI Use Cases & Tool Calling

### Tool 1: Create Order
- **Function**: `create_order(user_id, product, quantity)`
- **Input**: `"Order another mouse"` / `"I want 2 keyboards"`
- **Output**: `{"order_id": 104, "status": "Pending", "amount": 899.0}`

### Tool 2: Payment Processing
- **Function**: `pay_order(user_id, order_id)`
- **Input**: `"Pay for my latest order"` / `"Pay order 102"`
- **Output**: `{"status": "Success", "payment_id": "P102", "amount": 899.0}`

### Tool 3: Feedback & Sentiment Analysis
- **Function**: `submit_feedback(user_id, message, order_id)`
- **Input**: `"Packaging was poor. Box arrived crushed."`
- **Output**: 
  - Sentiment: `Negative`
  - Category: `Packaging`
  - Urgency: `High`
  - Response: `"We're deeply sorry to hear about your experience..."`

### Tool 4: Product Recommendations
- **Function**: `recommend_products(user_id, query_hint)`
- **Input**: `"Recommend laptop bags"`
- **Output**: Tailored list of complementary products with interactive buy chips.

---

## 6. Fake Database Schema

### Users Table
- `1`: John (`john@test.com` / `123456`)
- `2`: Alice (`alice@test.com` / `password`)
- `3`: Bob (`bob@test.com` / `abc123`)

### Orders Table
- `#101`: Keyboard | ₹1999 | Status: Delivered (User 1)
- `#102`: Mouse | ₹899 | Status: Pending (User 1)
- `#103`: Laptop Stand | ₹1599 | Status: Paid (User 1)
- `#104`: Wireless Headphones | ₹2999 | Status: Delivered (User 2)

### Payments Table
- `P101`: Order 101 | Method: Visa | Status: Paid | ₹1999
- `P103`: Order 103 | Method: Mastercard | Status: Paid | ₹1599

### Feedback Table
- `FeedbackID #1`: Order 101 | Message: *"Packaging was poor..."* | Sentiment: Negative | Category: Packaging | Urgency: High

---

## 7. REST APIs Table

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/login` | Authenticates user & returns JWT token |
| `GET` | `/orders` | Retrieves user's order history |
| `POST` | `/orders` | Creates a new order |
| `GET` | `/payments` | Retrieves payment transactions |
| `POST` | `/payment` | Processes order payment |
| `GET` | `/feedback` | Retrieves user feedback entries |
| `POST` | `/feedback` | Analyzes and stores feedback |
| `POST` | `/chat` | Conversational endpoint with AI tool invocation |
