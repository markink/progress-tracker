from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pymongo import MongoClient
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProgressLog(Base):
    __tablename__ = "progress_log"
    id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String, index=True)
    level = Column(Float)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

MONGO_URL = os.getenv("MONGO_URL")
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["tracker"]
skills_collection = mongo_db["skills"]

class Skill(BaseModel):
    name: str
    category: str
    subskills: Optional[List[str]] = []
    resources: Optional[List[str]] = []
    priority: Optional[str] = "medium"
    notes: Optional[str] = None

app = FastAPI(title="Progress Tracker API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/skills")
def add_skill(skill: Skill):
    skills_collection.insert_one(skill.dict())
    return {"status": "created", "skill": skill.name}

@app.get("/skills")
def list_skills(category: Optional[str] = None):
    query = {"category": category} if category else {}
    return list(skills_collection.find(query, {"_id": 0}))

@app.get("/skills/{name}")
def get_skill(name: str):
    skill = skills_collection.find_one({"name": name}, {"_id": 0})
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@app.post("/progress")
def add_progress(skill_name: str, level: float, comment: str = None,
                 db: Session = Depends(get_db)):
    log = ProgressLog(skill_name=skill_name, level=level, comment=comment)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@app.get("/progress")
def list_progress(db: Session = Depends(get_db)):
    return db.query(ProgressLog).all()

@app.get("/progress/{skill_name}")
def get_progress_by_skill(skill_name: str, db: Session = Depends(get_db)):
    return db.query(ProgressLog).filter(ProgressLog.skill_name == skill_name).all()
