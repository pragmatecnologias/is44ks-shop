# ResellOS

AI-powered product research and reselling intelligence platform for solo entrepreneurs.

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m unittest discover -s tests
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run build
npm run dev
```

## Docker

```bash
docker compose config
docker compose up --build
```

## Verified Checks

- `python -m compileall backend/app`
- `PYTHONPATH=. python -m unittest discover -s tests`
- `npm run build`
- `docker compose config`

## Architecture

- **backend/**: FastAPI + SQLAlchemy + PostgreSQL
- **frontend/**: Next.js 14 + Tailwind CSS + Radix UI
