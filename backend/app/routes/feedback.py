from pathlib import Path
from datetime import datetime

import pickle
import pandas as pd

from scipy.sparse import hstack

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException
)

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Feedback

from app.services.data_cleaning import clean_feedback_data
from app.services.language_detection import detect_language
from app.services.translation import translate_to_english
from app.services.topic_classification import classify_topic


router = APIRouter()


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# LOAD SENTIMENT MODEL
# ============================================================

# Current file:
# CivicLens/backend/app/routes/feedback.py
#
# Model folder:
# CivicLens/models/

BASE_DIR = Path(__file__).resolve().parents[3]

MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "sentiment_model.pkl"
WORD_VECTORIZER_PATH = MODEL_DIR / "word_vectorizer.pkl"
CHAR_VECTORIZER_PATH = MODEL_DIR / "char_vectorizer.pkl"


model = None
word_vectorizer = None
char_vectorizer = None


try:
    with open(MODEL_PATH, "rb") as file:
        model = pickle.load(file)

    with open(WORD_VECTORIZER_PATH, "rb") as file:
        word_vectorizer = pickle.load(file)

    with open(CHAR_VECTORIZER_PATH, "rb") as file:
        char_vectorizer = pickle.load(file)

    print("English sentiment model loaded successfully!")


except Exception as error:
    print(f"Error loading sentiment model: {error}")


# ============================================================
# SENTIMENT PREDICTION HELPER
# ============================================================

def predict_sentiment(comment: str):

    if (
        model is None
        or word_vectorizer is None
        or char_vectorizer is None
    ):
        raise HTTPException(
            status_code=500,
            detail="Sentiment model files could not be loaded."
        )

    # Word TF-IDF features
    word_features = word_vectorizer.transform([comment])

    # Character TF-IDF features
    char_features = char_vectorizer.transform([comment])

    # Combine both feature types
    combined_features = hstack(
        [word_features, char_features]
    ).tocsr()

    # Predict sentiment
    prediction = model.predict(combined_features)[0]

    # Get probabilities
    probabilities = model.predict_proba(
        combined_features
    )[0]

    class_probabilities = dict(
        zip(model.classes_, probabilities)
    )

    prediction_probability = class_probabilities[prediction]

    return {
        "sentiment": str(prediction),

        "probability": round(
            float(prediction_probability),
            4
        ),

        "confidence_percentage": round(
            float(prediction_probability) * 100,
            2
        ),

        "probabilities": {
            str(label): round(
                float(probability),
                4
            )

            for label, probability
            in class_probabilities.items()
        },

        "class_probabilities_percentage": {
            str(label): round(
                float(probability) * 100,
                2
            )

            for label, probability
            in class_probabilities.items()
        }
    }


# ============================================================
# GET ALL FEEDBACK
# ============================================================

@router.get("/")
def get_feedback(
    db: Session = Depends(get_db)
):

    feedback_list = db.query(Feedback).all()

    return [
        {
            "id": item.id,
            "comment_id": item.comment_id,
            "comment": item.comment,
            "language": item.language,
            "translated_comment": item.translated_comment,
            "predicted_sentiment":item.predicted_sentiment,
            "predicted_topic":item.predicted_topic,
            "topic_score": item.topic_score,
            "date": item.date,
            "location": item.location,
            "created_at": item.created_at
        }

        for item in feedback_list
    ]


# ============================================================
# ADD A SINGLE FEEDBACK
# ============================================================

@router.post("/")
def add_feedback(
    feedback: dict,
    db: Session = Depends(get_db)
):

    # Check duplicate comment_id
    existing_feedback = db.query(Feedback).filter(
        Feedback.comment_id == feedback["comment_id"]
    ).first()

    if existing_feedback:

        return {
            "error": (
                "Feedback with this comment_id "
                "already exists"
            )
        }

    comment = feedback["comment"].strip()

    if not comment:

        return {
            "error": "Comment cannot be empty"
        }

    # Detect language
    language = feedback.get("language")

    if not language:
        language = detect_language(comment)

    # Translate comment
    translated_comment = feedback.get(
        "translated_comment"
    )

    if not translated_comment:
        translated_comment = translate_to_english(
            comment,
            language
        )
    prediction_result = predict_sentiment(
    translated_comment
    )

    predicted_sentiment = prediction_result["sentiment"]
    topic_result = classify_topic(translated_comment)

    predicted_topic = topic_result["topic"]
    topic_score = topic_result["score"]

    # Parse date
    feedback_date = None

    if feedback.get("date"):

        try:
            feedback_date = datetime.strptime(
                feedback["date"],
                "%d-%m-%Y"
            ).date()

        except ValueError:

            return {
                "error": (
                    "Invalid date format. "
                    "Use DD-MM-YYYY."
                )
            }

    # Create database record
    new_feedback = Feedback(
        comment_id=feedback["comment_id"],
        comment=comment,
        language=language,
        translated_comment=translated_comment,
        predicted_sentiment=predicted_sentiment,
        date=feedback_date,
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
            "translated_comment": (
                new_feedback.translated_comment
            ),
            "predicted_sentiment": new_feedback.predicted_sentiment,
            "predicted_topic":new_feedback.predicted_topic,
            "topic_score" : new_feedback.topic_score,
            "date": new_feedback.date,
            "location": new_feedback.location
        }
    }
  # ============================================================
# BACKFILL MISSING SENTIMENTS
# ============================================================

def fill_missing_sentiments(db: Session):

    missing_feedback = (
        db.query(Feedback)
        .filter(
            Feedback.predicted_sentiment.is_(None)
        )
        .all()
    )

    updated_count = 0

    for feedback in missing_feedback:

        try:

            text_for_prediction = (
                feedback.translated_comment
                if feedback.translated_comment
                else feedback.comment
            )

            prediction_result = predict_sentiment(
                text_for_prediction
            )

            feedback.predicted_sentiment = (
                prediction_result["sentiment"]
            )

            updated_count += 1

            print(
                "BACKFILLED SENTIMENT:",
                feedback.comment_id,
                feedback.predicted_sentiment
            )

        except Exception as error:

            print(
                "FAILED TO PREDICT:",
                feedback.comment_id,
                str(error)
            )

    if updated_count > 0:
        db.commit()

    return updated_count




# ============================================================
# UPLOAD CSV / EXCEL
# ============================================================

@router.post("/upload")
async def upload_feedback(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # 1. Read uploaded file
    # --------------------------------------------------------

    if not file.filename:

        return {
            "error": "File name is missing"
        }

    filename = file.filename.lower()

    try:

        if filename.endswith(".csv"):

            df = pd.read_csv(file.file)

        elif filename.endswith((".xlsx", ".xls")):

            df = pd.read_excel(file.file)

        else:

            return {
                "error": (
                    "Only CSV and Excel files "
                    "are supported"
                )
            }

    except Exception as error:

        return {
            "error": f"Could not read file: {str(error)}"
        }

    # --------------------------------------------------------
    # 2. Check empty file
    # --------------------------------------------------------

    if df.empty:

        return {
            "error": "The uploaded file is empty"
        }

    # --------------------------------------------------------
    # 3. Clean data
    # --------------------------------------------------------

    try:

        df = clean_feedback_data(df)

    except Exception as error:

        return {
            "error": f"Error cleaning data: {str(error)}"
        }

    # --------------------------------------------------------
    # 4. Check required columns
    # --------------------------------------------------------

    required_columns = {
        "comment"
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:

        return {
            "error": "Missing required columns",
            "missing_columns": list(missing_columns)
        }

    # --------------------------------------------------------
    # 5. Find next comment_id
    # --------------------------------------------------------

    last_feedback = (
        db.query(Feedback)
        .order_by(Feedback.comment_id.desc())
        .first()
    )

    if last_feedback:

        next_comment_id = (
            last_feedback.comment_id + 1
        )

    else:

        next_comment_id = 1

    saved_count = 0
    skipped_count = 0

    # --------------------------------------------------------
    # 6. Process each row
    # --------------------------------------------------------

    for _, row in df.iterrows():

        # Get comment
        if pd.isna(row["comment"]):

            skipped_count += 1
            continue

        comment = str(row["comment"]).strip()

        # Skip empty comments
        if not comment:

            skipped_count += 1
            continue

        # ----------------------------------------------------
        # Generate or use comment_id
        # ----------------------------------------------------

        if (
            "comment_id" in df.columns
            and pd.notna(row["comment_id"])
        ):

            try:

                comment_id = int(
                    row["comment_id"]
                )

            except (ValueError, TypeError):

                skipped_count += 1
                continue

        else:

            comment_id = next_comment_id
            next_comment_id += 1

        # ----------------------------------------------------
        # Check duplicate comment_id
        # ----------------------------------------------------

        existing_feedback = db.query(Feedback).filter(
            Feedback.comment_id == comment_id
        ).first()

        if existing_feedback:

            skipped_count += 1
            continue

        # ----------------------------------------------------
        # Detect language
        # ----------------------------------------------------

        language = detect_language(comment)

        # ----------------------------------------------------
        # Translate to English
        # ----------------------------------------------------

        translated_comment = translate_to_english(
            comment,
            language
        )
        prediction_result = predict_sentiment(
        translated_comment
        )

        predicted_sentiment = prediction_result["sentiment"]

        # ----------------------------------------------------
        # Process date
        # ----------------------------------------------------

        feedback_date = None

        if (
            "date" in df.columns
            and pd.notna(row["date"])
        ):

            raw_date = row["date"]

            try:

                if hasattr(raw_date, "date"):

                    feedback_date = raw_date.date()

                else:

                    feedback_date = datetime.strptime(
                        str(raw_date),
                        "%d-%m-%Y"
                    ).date()

            except ValueError:

                skipped_count += 1
                continue

        # ----------------------------------------------------
        # Process location
        # ----------------------------------------------------

        if (
            "location" in df.columns
            and pd.notna(row["location"])
        ):

            location = str(
                row["location"]
            ).strip()

        else:

            location = None

        # ----------------------------------------------------
        # Create database record
        # ----------------------------------------------------

        new_feedback = Feedback(
            comment_id=comment_id,
            comment=comment,
            language=language,
            translated_comment=translated_comment,
            predicted_sentiment=predicted_sentiment,
            predicted_topic=predicted_topic,
            topic_score=topic_score,
            date=feedback_date,
            location=location
        )
        db.add(new_feedback)

        print(
            "SAVING FEEDBACK:",
            comment_id,
            comment,
            predicted_sentiment
        )

        saved_count += 1
        

    # --------------------------------------------------------
    # 7. Save records
    # --------------------------------------------------------

    try:

        db.commit()

    except Exception as error:

        db.rollback()

        return {
            "error": (
                f"Database error: {str(error)}"
            )
        }

    # --------------------------------------------------------
    # 8. Return response
    # --------------------------------------------------------

    return {
        "filename": file.filename,
        "rows": len(df),
        "saved_to_database": saved_count,
        "skipped_rows": skipped_count,
        "data": df.to_dict(
            orient="records"
        )
    }


# ============================================================
# SENTIMENT PREDICTION ENDPOINT
# ============================================================

class FeedbackPredictionRequest(BaseModel):

    comment: str


@router.post("/predict")
def predict_feedback(
    request: FeedbackPredictionRequest
):
    comment = request.comment.strip()

    if not comment:
        raise HTTPException(
            status_code=400,
            detail="Comment cannot be empty."
        )

    prediction_result = predict_sentiment(
        comment
    )

    return {
        "comment": comment,
        **prediction_result
    }