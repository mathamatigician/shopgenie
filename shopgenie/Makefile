# ShopGenie Subdirectory Makefile
.PHONY: help install seed backend frontend test run clean

PYTHON = venv/bin/python
UVICORN = venv/bin/uvicorn
VENV = venv

help:
	@echo "ShopGenie AI Commerce Commands:"
	@echo "  make install   - Install backend Python venv and frontend npm dependencies"
	@echo "  make seed      - Reset & seed database with initial users, orders, payments"
	@echo "  make backend   - Start FastAPI backend server on port 8000"
	@echo "  make frontend  - Start VueJS frontend dev server on port 3000"
	@echo "  make test      - Run automated API & AI tool calling tests"
	@echo "  make clean     - Remove database & generated build files"

install:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install fastapi uvicorn sqlalchemy pyjwt pydantic python-multipart google-genai
	cd frontend && npm install

seed:
	PYTHONPATH=backend $(PYTHON) database/seed.py

backend:
	PYTHONPATH=backend $(UVICORN) app:app --reload --host 0.0.0.0 --port 8000 --app-dir backend

frontend:
	cd frontend && npm run dev

test:
	PYTHONPATH=backend $(PYTHON) /home/harsh/.gemini/antigravity-cli/brain/ffe54e50-6bf7-4aab-9365-23e536c99b87/scratch/test_backend.py

clean:
	rm -f backend/shopgenie.db
	rm -rf frontend/dist
