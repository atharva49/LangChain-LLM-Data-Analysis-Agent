# ChatGPT SQL Agent

Conversational SQL Agent: natural-language querying of a sales SQLite dataset using LangChain/OpenAI, FastAPI backend, and a React frontend. The project is fully Dockerized and includes a deterministic Faker-based seeder so you can reproduce demo data locally.

---

## Features
- Natural-language → SQL using LangChain and OpenAI
- FastAPI backend exposing a single `/query` endpoint
- React frontend for conversational queries and result display
- Docker Compose for local development
- Deterministic seeder (`backend/app/seed_db.py`) that writes to `backend/data/sales.db`

## Tech stack
- Python, FastAPI, LangChain, OpenAI
- React (frontend)
- SQLite (seeded dataset)
- Docker Compose

## Quickstart (Docker — recommended)
1. Copy or set environment variables (see `backend/.env.example`):

   - `OPENAI_API_KEY` — your OpenAI API key
   - `SQLITE_DB_PATH` — optional custom path (defaults to `./data/sales.db` inside backend)

2. Build and start services:

```powershell
cd 'e:\VSCODE\LLM_projects\chatgpt-sql-agent-fastapi-react'
docker compose up --build -d
```

3. Seed the database (writes to `backend/data/sales.db`):

```powershell
docker compose run --rm backend python app/seed_db.py
```

4. Open the frontend at http://localhost:3000 and try a sample query, or call the API:

```powershell
# Example using PowerShell
Invoke-RestMethod -Method POST -Uri http://localhost:8000/query -ContentType 'application/json' -Body (@{question='Total revenue by region in 2024'} | ConvertTo-Json)
```

## Local (no Docker)
1. Create a virtualenv and install requirements:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

2. Seed DB and run backend:

```powershell
setx OPENAI_API_KEY "your_key_here"
cd backend
python app/seed_db.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Start the frontend (from `frontend/`):

```powershell
cd frontend
npm install
npm start
```

## API
- POST /query
  - Request JSON: { "question": "<natural language question>" }
  - Response JSON: { "answer": "<agent output / SQL / result>" }

Example request/response:

```json
POST /query
{
  "question": "What was the total revenue by product in Q3 2024?"
}

Response:
{
  "answer": "...agent output..."
}
```

## Sample queries to try
- "Total revenue by region for 2024"
- "Top 5 products by revenue in September 2024"
- "Show me transactions for customer_id 10"
- "Average order value by month"

## Screenshots / Demo
Add screenshots or a short GIF here showing the frontend in action and a sample query/response.

![screenshot-placeholder](./docs/screenshot-1.png)

## Security & Limitations
- The project uses an LLM to generate SQL — review generated SQL before running in production. For demos, we seed a local SQLite DB and run queries read-only.
- Be careful not to commit `backend/data/sales.db` or any `.env` files with secrets. Add `backend/data/` and `.env` to `.gitignore`.

## Contributing
- PRs welcome. For larger changes open an issue first.

## License
MIT — choose a license file if you want to publish.

---

If you'd like, I can add a simple `docs/` folder with demo screenshots, or commit a `.gitignore` and an initial commit for you.
# ChatGPT + LangChain + SQLite + FastAPI + React (Dockerized)

This project demonstrates a minimal setup where a user asks natural-language
questions from a React frontend. A FastAPI backend uses LangChain + OpenAI
to translate questions into SQL, run them against a local SQLite database,
and return natural language answers.

## Features
- FastAPI backend with `/query` endpoint
- LangChain SQL agent that queries SQLite (`data/sales.db`)
- Automatic DB seeding on startup (sample `sales` table)
- React frontend (Create-React-App style) that calls the backend
- Docker Compose to run both services

## Quickstart (local)
1. Copy `.env.example` to `.env` and set your `OPENAI_API_KEY`.
2. Build and run with Docker Compose:
   ```bash
   docker compose up --build
   ```
3. Open the frontend:
   - http://localhost:3000
4. Ask a question like:
   - `What is the total revenue in Texas?`
   - `Show total revenue by region.`

## Notes
- The backend uses LangChain. LangChain versions change frequently; pinned versions in `backend/requirements.txt` are known to work as of the creation of this project.
- Keep your OpenAI key secret. Do not check `.env` into source control.
>>>>>>> b1a04fa (Initial commit: chatgpt-sql-agent-fastapi-react)
