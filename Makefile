# ShopGenie Makefile
.PHONY: help install seed backend frontend test run clean

PYTHON = shopgenie/venv/bin/python
UVICORN = shopgenie/venv/bin/uvicorn
VENV = shopgenie/venv

help:
	@echo "ShopGenie AI Commerce Commands:"
	@echo "  make install   - Install backend Python venv and frontend npm dependencies"
	@echo "  make seed      - Reset & seed database with initial users, orders, payments"
	@echo "  make backend   - Start FastAPI backend server on port 8000"
	@echo "  make frontend  - Start VueJS frontend dev server on port 3000"
	@echo "  make test      - Run automated API & AI tool calling tests"
	@echo "  make run       - Seed DB & start both backend and frontend servers"
	@echo "  make clean     - Remove database & generated build files"

install:
	@echo "Setting up Python virtual environment..."
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install fastapi uvicorn sqlalchemy pyjwt pydantic python-multipart google-genai
	@echo "Installing Frontend dependencies..."
	cd shopgenie/frontend && npm install

seed:
	@echo "Seeding database..."
	PYTHONPATH=shopgenie/backend $(PYTHON) shopgenie/database/seed.py

backend:
	@echo "Starting FastAPI Backend Server..."
	PYTHONPATH=shopgenie/backend $(UVICORN) app:app --reload --host 0.0.0.0 --port 8000 --app-dir shopgenie/backend

frontend:
	@echo "Starting VueJS Frontend Server..."
	cd shopgenie/frontend && npm run dev

test:
	@echo "Running API & AI Tool Calling Tests..."
	PYTHONPATH=shopgenie/backend $(PYTHON) /home/harsh/.gemini/antigravity-cli/brain/ffe54e50-6bf7-4aab-9365-23e536c99b87/scratch/test_backend.py

run: seed
	@echo "Launching ShopGenie Stack..."
	PYTHONPATH=shopgenie/backend $(UVICORN) app:app --host 0.0.0.0 --port 8000 --app-dir shopgenie/backend &
	cd shopgenie/frontend && npm run dev

clean:
	rm -f shopgenie/backend/shopgenie.db
	rm -rf shopgenie/frontend/dist
	@echo "Clean completed."
