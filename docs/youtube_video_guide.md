# YouTube Video Guide & Script for ShopGenie 🧞‍♂️

A step-by-step guide and video script to record a YouTube video showcasing ShopGenie.

---

## 🎬 1. Preparation & Setup

### A. Free Recording Software
- **OBS Studio** (Recommended - Open Broadcaster Software) or **OS Screen Recorder** / **Loom**.
- Set canvas resolution to **1080p (1920x1080)** or **4K (3840x2160)**.
- Ensure your microphone is enabled so you can demo the **Voice Command Feature**.

### B. Launch ShopGenie Stack
Open terminal and launch both backend & frontend using the Makefile:
```bash
make run
```
- **Backend**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000`

---

## 📜 2. Winning YouTube Video Script (3-4 Minutes)

### **Part 1: The Hook & Problem Statement (0:00 - 0:30)**
- **Visual**: Show traditional Amazon/Flipkart multi-tab screens (search, checkout forms, payment screens).
- **Voiceover**: 
  > *"Have you ever gotten tired of navigating through 10 different screens just to order a snack or pay a bill online? Traditional e-commerce platforms have too much friction—especially for elderly, mobile, and visually impaired users. Today, I'm showing you **ShopGenie**—an AI-first e-commerce app where you complete your entire shopping experience purely through conversation!"*

---

### **Part 2: 1-Click Login & Dashboard Overview (0:30 - 0:55)**
- **Visual**: Show ShopGenie Login page (`http://localhost:3000/login`). Click the **John** quick fill button (`john@test.com` / `123456`) and click **Sign In**. Show the sleek glassmorphic Dashboard.
- **Voiceover**: 
  > *"Let's sign in as John. ShopGenie instantly generates a secure JWT token. On the Dashboard, we can see active orders, payment statuses, and quick prompt chips."*

---

### **Part 3: Conversational Product Search & Draft Confirmation (0:55 - 1:30)**
- **Visual**: Navigate to **AI Assistant** (`/chat`). Type or speak:
  `"Create a new order for 2 icecereams 100 ml each. Amul brand only."`
- **Show Response**: Show the AI listing available Amul Vanilla/Mango ice cream cups with item prices and total cost (₹100.00).
- **Type/Speak**: `"Yes, confirm and pay"`
- **Voiceover**: 
  > *"Instead of immediately forcing an order, ShopGenie checks inventory, displays item breakdowns, shows alternate variants, and asks for payment confirmation. Once confirmed, it executes order creation AND processes payment via Visa in 1 step!"*

---

### **Part 4: Multi-Item Inventory Check & Alternate Options (1:30 - 2:15)**
- **Visual**: Type or speak:
  `"Create an order for 1. Amul 500g ice-cream pack 1 Qty 2. Balaji Potato Chips 20 Rs pack 5 Qty."`
- **Show Response**: Show the AI detecting that 500g packs and Balaji brand chips are out of stock, and listing available in-store alternates (*Lays Chips*, *Bingo Chips*).
- **Voiceover**: 
  > *"Watch how ShopGenie handles complex multi-item prompts. When requested items or sizes are out of stock, it reports availability per item and suggests in-store alternatives item-by-item!"*

---

### **Part 5: Show Cart, Update Quantity & Sorting (2:15 - 2:50)**
- **Visual**: 
  1. Type: `"show cart option"`
  2. Type: `"Update quantity of Amul Vanilla Ice Cream to 5"`
  3. Type: `"List Amul mango ice-creams sorted by price"`
- **Voiceover**: 
  > *"You can inspect your current cart draft anytime with 'show cart option', update item quantities dynamically, or list products sorted from lowest to highest price!"*

---

### **Part 6: Voice Accessibility & AI Sentiment Feedback (2:50 - 3:30)**
- **Visual**: 
  1. Click the **Microphone Icon** 🎙️ and speak: `"List past orders having ice-cream"`.
  2. Toggle **Speech Output** 🔊 to hear the audio response.
  3. Type: `"Packaging was poor for order 101. The box arrived crushed."`
- **Show Response**: Show AI analyzing Sentiment (*Negative*), Category (*Packaging*), Urgency (*High*), and generating an apology response.
- **Voiceover**: 
  > *"For accessibility, users can speak into the microphone or listen to voice output. And for customer support, instead of star ratings, ShopGenie uses NLP sentiment analysis to extract category and urgency automatically!"*

---

### **Part 7: Conclusion & Call to Action (3:30 - 3:45)**
- **Visual**: Show project GitHub repo or summary screen.
- **Voiceover**: 
  > *"That is **ShopGenie**—making e-commerce zero-friction and accessible to everyone. If you enjoyed this project, don't forget to like, subscribe, and star the GitHub repository below!"*

---

## 🛠️ 3. Recommended Video Tags & Description

### Title Suggestions:
- 🧞‍♂️ **ShopGenie: AI-First Conversational E-Commerce (FastAPI, Vue 3 & Tool Calling)**
- 🚀 **I Built an AI Shopping Assistant that Replaces Amazon's GUI with Conversation!**

### Description Text:
```
ShopGenie is an AI-first conversational e-commerce web application built with FastAPI, SQLite, Vue 3, and AI Tool Calling.

✨ Key Features:
- Conversational Shopping & Payment Execution
- Multi-Item Inventory Checking & Alternate Product Suggestions
- Voice Input (Web Speech API) & Speech Output
- NLP Sentiment Analysis for Customer Feedback
- Dynamic CSV Database Seeding

Tech Stack: FastAPI, Vue 3, Vite, SQLite, PyJWT, Tailwind/Glassmorphism CSS.
```
