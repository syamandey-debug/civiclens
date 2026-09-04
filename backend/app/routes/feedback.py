from fastapi import APIRouter, UploadFile, File
import pandas as pd
from pathlib import Path

router = APIRouter()


@router.get("/")
def get_feedback():

    csv_path = Path(__file__).resolve().parents[3] / "data" / "feedback.csv"

    df = pd.read_csv(csv_path)

    return df.to_dict(orient="records")


@router.post("/")
def add_feedback(feedback: dict):

    return {
        "message": "Feedback received",
        "feedback": feedback
    }


@router.post("/upload")
async def upload_feedback(file: UploadFile = File(...)):

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)

    elif file.filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file.file)

    else:
        return {
            "error": "Only CSV and Excel files are supported"
        }

    return {
        "filename": file.filename,
        "rows": len(df),
        "data": df.to_dict(orient="records")
    }