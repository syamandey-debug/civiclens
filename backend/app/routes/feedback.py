from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import pandas as pd
from pathlib import Path

from app.database import SessionLocal
from app.models import Feedback

router = APIRouter()


# Database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_feedback(db: Session = Depends(get_db)):

    feedback_list = db.query(Feedback).all()

    return [
        {
            "id": item.id,
            "original_text": item.original_text,
            "created_at": item.created_at
        }
        for item in feedback_list
    ]


@router.post("/")
def add_feedback(feedback: dict, db: Session = Depends(get_db)):

    new_feedback = Feedback(
        original_text=feedback["original_text"]
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    return {
        "message": "Feedback saved successfully",
        "feedback": {
            "id": new_feedback.id,
            "original_text": new_feedback.original_text
        }
    }


@router.post("/upload")
async def upload_feedback(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)

    elif file.filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file.file)

    else:
        return {
            "error": "Only CSV and Excel files are supported"
        }

    saved_count = 0

    for _, row in df.iterrows():

        # Change "feedback" if your CSV uses a different column name
        if "comment" in df.columns:
            text = row["comment"]

            new_feedback = Feedback(
                original_text=str(text)
            )

            db.add(new_feedback)
            saved_count += 1

    db.commit()

    return {
        "filename": file.filename,
        "rows": len(df),
        "saved_to_database": saved_count,
        "data": df.to_dict(orient="records")
    }