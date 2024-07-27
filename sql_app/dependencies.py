# dependencies.py
from sqlalchemy.orm import Session
from fastapi import Depends
from database import SessionLocal

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
