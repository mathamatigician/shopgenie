import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from models import User

import auth
import orders
import payments
import feedback
import chat

app = FastAPI(
    title="ShopGenie Backend API",
    description="AI-First Conversational Ecommerce API with Tool Calling",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(feedback.router)
app.include_router(chat.router)

@app.on_event("startup")
def startup_event():
    # Ensure database schema is initialized and seeded if empty
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            print("Database empty. Seeding initial data...")
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database")))
            from seed import seed_db
            seed_db()
    except Exception as e:
        print(f"Startup check failed: {e}")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "ShopGenie AI-First Ecommerce API",
        "version": "1.0.0",
        "endpoints": {
            "login": "POST /login",
            "orders": "GET /orders, POST /orders",
            "payment": "POST /payment, GET /payments",
            "feedback": "POST /feedback, GET /feedback",
            "chat": "POST /chat"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
