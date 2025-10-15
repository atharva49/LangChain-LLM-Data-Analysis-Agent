<<<<<<< HEAD
# LangChain-LLM-Data-Analysis-Agent
LLM SQL Agent provides a conversational interface to query sales data. The backend (FastAPI + LangChain) translates natural-language questions into safe SQL, runs them against an embedded SQLite dataset, and the React frontend displays results. Docker Compose included for local development
=======
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
