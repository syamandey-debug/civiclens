from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import feedback
from app.routes.feedback import fill_missing_sentiments
from app.database import engine, Base, SessionLocal
from app import models


app = FastAPI()


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# AUTOMATIC SENTIMENT BACKFILL
# ============================================================

@app.on_event("startup")
def run_sentiment_backfill():

    db = SessionLocal()

    try:

        updated_count = fill_missing_sentiments(db)

        print(
            f"Sentiment backfill completed: "
            f"{updated_count} records updated."
        )

    except Exception as error:

        print(
            f"Sentiment backfill failed: {str(error)}"
        )

    finally:

        db.close()


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# FEEDBACK ROUTES
# ============================================================

app.include_router(
    feedback.router,
    prefix="/feedback",
    tags=["Feedback"]
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "CivicLens Backend is working!"
    }


# ============================================================
# API TEST
# ============================================================

@app.get("/api/test")
def test():

    return {
        "message": "Frontend and Backend connected!"
    }
