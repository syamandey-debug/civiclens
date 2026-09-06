from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime

from app.database import SessionLocal
from app.models import Feedback
from app.services.data_cleaning import clean_feedback_data

router = APIRouter()


# Database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Get all feedback
@router.get("/")
def get_feedback(db: Session = Depends(get_db)):

    feedback_list = db.query(Feedback).all()

    return [
        {
            "id": item.id,
            "comment_id": item.comment_id,
            "comment": item.comment,
            "language": item.language,
            "date": item.date,
            "location": item.location,
            "created_at": item.created_at
        }
        for item in feedback_list
    ]


# Add a single feedback
@router.post("/")
def add_feedback(
    feedback: dict,
    db: Session = Depends(get_db)
):

    new_feedback = Feedback(
        comment_id=feedback["comment_id"],
        comment=feedback["comment"],
        language=feedback.get("language"),
        date=datetime.strptime(
            feedback["date"], "%d-%m-%Y"
        ).date() if feedback.get("date") else None,
        location=feedback.get("location")
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    return {
        "message": "Feedback saved successfully",
        "feedback": {
            "id": new_feedback.id,
            "comment_id": new_feedback.comment_id,
            "comment": new_feedback.comment,
            "language": new_feedback.language,
            "date": new_feedback.date,
            "location": new_feedback.location
        }
    }


# Upload CSV / Excel
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
    df = clean_feedback_data(df)
    # Check required columns
    required_columns = {
        "comment_id",
        "comment",
        "language",
        "date",
        "location"
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        return {
            "error": "Missing required columns",
            "missing_columns": list(missing_columns)
        }

    saved_count = 0

    for _, row in df.iterrows():

        comment = str(row["comment"]).strip()

        if not comment:
            continue

        feedback_date = None

        if pd.notna(row["date"]):
            feedback_date = datetime.strptime(
                str(row["date"]),
                "%d-%m-%Y"
            ).date()
        comment_id = int(row["comment_id"])

        existing_feedback = db.query(Feedback).filter(
        Feedback.comment_id == comment_id
        ).first()

        if existing_feedback:
            continue
        existing_feedback = db.query(Feedback).filter(
           Feedback.comment_id == feedback["comment_id"]
        ).first()

        if existing_feedback:
            return {
                "error": "Feedback with this comment_id already exists"
            }
        new_feedback = Feedback(
            comment_id=comment_id,
            comment=comment,
            language=(
                str(row["language"]).strip()
                if pd.notna(row["language"])
                else None
            ),
            date=feedback_date,
            location=(
                str(row["location"]).strip()
                if pd.notna(row["location"])
                else None
            )
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