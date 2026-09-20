from pathlib import Path

import pandas as pd
from datasets import load_dataset


# -----------------------------------
# 1. Load the Hugging Face dataset
# -----------------------------------

print("Loading dataset...")

dataset = load_dataset(
    "dhruv0808/indic_sentiment_analyzer"
)

df = dataset["train"].to_pandas()

print("Original dataset size:", len(df))


# -----------------------------------
# 2. English language detection
# -----------------------------------

def contains_latin(text):
    """
    Detect Latin alphabet characters.
    """

    return any(
        ("A" <= char <= "Z") or
        ("a" <= char <= "z")
        for char in text
    )


def detect_language(text):
    """
    Detect English text only.

    Returns None for non-English text.
    """

    if not isinstance(text, str):
        return None

    # English text must contain Latin characters
    if contains_latin(text):
        return "English"

    return None


# -----------------------------------
# 3. Detect language
# -----------------------------------

print("Detecting English language...")

df["language"] = df["Sentence"].apply(
    detect_language
)


# -----------------------------------
# 4. Keep only English
# -----------------------------------

df = df[
    df["language"] == "English"
].copy()


# -----------------------------------
# 5. Rename columns
# -----------------------------------

df = df.rename(
    columns={
        "Sentence": "comment",
        "Label": "sentiment"
    }
)


# -----------------------------------
# 6. Keep required columns
# -----------------------------------

df = df[
    ["comment", "language", "sentiment"]
]


# -----------------------------------
# 7. Clean the data
# -----------------------------------

df["comment"] = (
    df["comment"]
    .astype(str)
    .str.strip()
)

df["language"] = (
    df["language"]
    .astype(str)
    .str.strip()
)

df["sentiment"] = (
    df["sentiment"]
    .astype(str)
    .str.strip()
)

df = df[
    df["comment"] != ""
]

df = df.drop_duplicates(
    subset=[
        "comment",
        "language",
        "sentiment"
    ]
)


# -----------------------------------
# 8. Display statistics
# -----------------------------------

print("\nSelected English dataset size:", len(df))

print("\nLanguage distribution:")
print(df["language"].value_counts())

print("\nSentiment distribution:")
print(df["sentiment"].value_counts())

print("\nSentiment distribution:")
print(df["sentiment"].value_counts())


# -----------------------------------
# 9. Save the prepared dataset
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_PATH = DATA_DIR / "training_data.csv"

df.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("\nEnglish dataset saved successfully!")
print("Saved location:", OUTPUT_PATH)