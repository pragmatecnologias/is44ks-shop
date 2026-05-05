# ResellOS

AI-powered product research and reselling intelligence platform for solo entrepreneurs.

## Quick Start

```bash
# Backend
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Docker

```bash
docker-compose up --build
```

## Architecture

- **backend/**: FastAPI + SQLAlchemy + PostgreSQL
- **frontend/**: Next.js 14 + Tailwind CSS + Radix UI