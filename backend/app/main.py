from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import feedback
from app.database import engine,Base
from app import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Allow React frontend to communicate with FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
@app.get("/")
def home():
    return {"message": "CivicLens Backend is working!"}


@app.get("/api/test")
def test():
    return {"message": "Frontend and Backend connected!"}