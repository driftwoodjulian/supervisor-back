from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Source DB (Postgres)
SOURCE_DB_URI = os.getenv("SOURCE_DB_URI")
source_engine = create_engine(SOURCE_DB_URI)
SourceSession = scoped_session(sessionmaker(bind=source_engine))
SourceBase = declarative_base()

# Evaluations DB (SQLite) - For Users
EVAL_DB_URI = os.getenv("EVAL_DB_URI")
eval_engine = create_engine(EVAL_DB_URI)
EvalSession = scoped_session(sessionmaker(bind=eval_engine))
EvalBase = declarative_base()

# HITL Evaluations DB (SQLite) - Separated as per request
HITL_EVAL_DB_URI = os.getenv("HITL_EVAL_DB_URI", "sqlite:///hitl_evaluations.db")
hitl_eval_engine = create_engine(HITL_EVAL_DB_URI)
HitlEvalSession = scoped_session(sessionmaker(bind=hitl_eval_engine))
HitlEvalBase = declarative_base()

def init_db():
    EvalBase.metadata.create_all(eval_engine)
    HitlEvalBase.metadata.create_all(hitl_eval_engine)

SessionLocal = EvalSession
engine = eval_engine
SourceSessionLocal = SourceSession
