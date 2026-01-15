# DivinaPopinaV2

## Project Overview

DivinaPopinaV2 is a full-stack mock e-commerce platform designed to demonstrate professional-grade architecture, code quality, and deployment hygiene. This project is intended for client demonstration and technical review, not for production use.

**Key Features:**
- Modern React frontend with API-only data access
- Python backend (Quart, SQLAlchemy) with clear domain boundaries
- Explicit mock boundaries for all financial, payment, and shipment operations
- Professional .gitignore and repo hygiene
- Demonstrates error handling, loading/empty states, and maintainable structure

---

## Mock Project Notice

> **All financial, shipment, and payment operations in this project are mocked.**
>
> - No real money, payment, or shipment transactions occur.
> - Domain logic is real; all external side effects are simulated.
> - This is intentional for demonstration and client review purposes.

---

## Repository Structure

```
divinaPopinaV2/
├── backend/           # Python backend (Quart, SQLAlchemy)
│   ├── app.py         # Main backend app
│   ├── api/           # API routes only
│   ├── services/      # Business logic only
│   ├── repositories/  # DB access only
│   ├── models/        # ORM only
│   ├── schemas/       # Pydantic only
│   ├── infrastructure/# Email, storage, external APIs
│   └── ...
├── frontend/          # React frontend
│   ├── public/
│   └── src/
├── .env.example       # Example environment variables
├── .gitignore         # Git ignore rules
├── README.md          # Project overview and instructions
├── ARCHITECTURE.md    # Architecture and boundaries
├── SECURITY.md        # Security model and practices
└── ...
```

---

## Setup

1. Clone the repository
2. Create a virtual environment and install dependencies:
   ```sh
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in required environment variables.

## Environments
- ENV=dev|test|prod (set in .env)

## Run
- Backend: `python -m backend.app`
- Frontend: `cd frontend && npm install && npm start`

## Test
- Backend: `pytest`
- Frontend: `cd frontend && npm test`

## Deploy
- See ARCHITECTURE.md and SECURITY.md for deployment and security notes.

---

## Professional Review Checklist

- [x] No node_modules or build artifacts in repo
- [x] .gitignore covers all environments
- [x] Mock boundaries are explicit and documented
- [x] API layer is the only data entry for frontend
- [x] No inline mock data or hardcoded arrays in components
- [x] All pages handle loading, error, and empty states
- [x] Folder names and structure are correct and professional

---

## For Clients & Reviewers

This project is intentionally structured to demonstrate:
- Clean separation of concerns
- Professional repo hygiene
- Explicit mock boundaries
- Readiness for real-world extension

If you have questions or want to see a real integration, please contact the maintainer.
