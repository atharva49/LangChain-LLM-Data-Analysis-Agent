import os
from functools import lru_cache
from dotenv import load_dotenv
load_dotenv()
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI

import sqlite3

import pathlib

# Import the project's seeder. Use relative import when possible but fall back to absolute.
try:
    from . import seed_db
except Exception:
    import seed_db


def ensure_db_seeded(sqlite_path: str = "./data/sales.db"):
    """Ensure the sqlite DB exists. If not, run the project's seeder (seed_db.seed_main).

    This sets SQLITE_DB_PATH so the seeder writes to the requested path. If the
    seeder or Faker is not available, the error is printed and the function returns.
    """
    # make sure the seeder writes to the same path we will use
    os.environ['SQLITE_DB_PATH'] = sqlite_path
    path = pathlib.Path(sqlite_path)
    if path.exists():
        return
    try:
        print(f"Seeding database at {sqlite_path}...")
        seed_db.seed_main()
        print("Seeding complete.")
    except Exception as e:
        # don't raise here; caller may want to continue and surface the error
        print(f"Warning: failed to seed database at {sqlite_path}: {e}")

@lru_cache(maxsize=1)
def create_agent(sqlite_path: str = "./data/sales.db", openai_api_key: str = None):
    if openai_api_key:
        os.environ['OPENAI_API_KEY'] = openai_api_key
    # ensure the DB exists and is seeded before creating the SQL agent
    try:
        ensure_db_seeded(sqlite_path)
    except Exception:
        # ensure_db_seeded is defensive, but catch any unexpected issues here
        pass
    # Construct SQLAlchemy URI for sqlite for langchain
    db_uri = f"sqlite:///{os.path.abspath(sqlite_path)}"
    db = SQLDatabase.from_uri(db_uri)
    # choose an LLM model - change model name to match your OpenAI access
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent = create_sql_agent(llm=llm, toolkit=toolkit, verbose=False)
    return agent
