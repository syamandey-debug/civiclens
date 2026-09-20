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
# 2. Language detection functions
# -----------------------------------

def contains_devanagari(text):
    """
    Detect Hindi-style Devanagari characters.
    Unicode range: U+0900 to U+097F
    """

    return any(
        "\u0900" <= char <= "\u097F"
        for char in text
    )


def contains_telugu(text):
    """
    Detect Telugu characters.
    Unicode range: U+0C00 to U+0C7F
    """

    return any(
        "\u0C00" <= char <= "\u0C7F"
        for char in text
    )


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
    Identify English, Hindi, or Telugu.

    Returns None for unsupported or
    ambiguous scripts.
    """

    if not isinstance(text, str):
        return None

    if contains_devanagari(text):
        return "Hindi"

    if contains_telugu(text):
        return "Telugu"

    if contains_latin(text):
        return "English"

    return None


# -----------------------------------
# 3. Detect language
# -----------------------------------

print("Detecting languages...")

df["language"] = df["Sentence"].apply(
    detect_language
)


# -----------------------------------
# 4. Keep only required languages
# -----------------------------------

selected_languages = [
    "English",
    "Hindi",
    "Telugu"
]

df = df[
    df["language"].isin(selected_languages)
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

print("\nSelected dataset size:", len(df))

print("\nLanguage distribution:")
print(df["language"].value_counts())

print("\nSentiment distribution:")
print(df["sentiment"].value_counts())

print("\nLanguage and sentiment distribution:")
print(
    pd.crosstab(
        df["language"],
        df["sentiment"]
    )
)


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

print("\nDataset saved successfully!")
print("Saved location:", OUTPUT_PATH)