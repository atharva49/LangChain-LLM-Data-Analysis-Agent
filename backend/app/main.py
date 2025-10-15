import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

load_dotenv()

from .agent import create_agent#, ensure_db_seeded

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "./data/sales.db")

app = FastAPI(title="ChatGPT SQL Agent (FastAPI)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn.error")

class QueryRequest(BaseModel):
    question: str

# On startup, ensure DB exists and agent is created once
@app.on_event("startup")
async def startup_event():
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set in environment.")
    # ensure DB file and seed data
    #ensure_db_seeded(SQLITE_DB_PATH)
    # create agent (cached inside create_agent)
    create_agent(sqlite_path=SQLITE_DB_PATH, openai_api_key=OPENAI_API_KEY)

@app.post("/query")
async def query_endpoint(req: QueryRequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="question required")

    try:
        agent = create_agent(sqlite_path=SQLITE_DB_PATH, openai_api_key=OPENAI_API_KEY)
        # call the agent's run method
        result = agent.run(req.question)
        return {"answer": result}
    except Exception as e:
        logger.exception("Error running agent")
        raise HTTPException(status_code=500, detail=str(e))
