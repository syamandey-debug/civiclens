import os
import pickle
import warnings

import numpy as np
import pandas as pd

from scipy.sparse import hstack

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score
)

warnings.filterwarnings("ignore")


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "training_data.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

os.makedirs(MODEL_DIR, exist_ok=True)


MODEL_PATH = os.path.join(
    MODEL_DIR,
    "sentiment_model.pkl"
)

WORD_VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "word_vectorizer.pkl"
)

CHAR_VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "char_vectorizer.pkl"
)


# ============================================================
# 2. LOAD DATASET
# ============================================================

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Original dataset size: {len(df)}")
print(f"Columns: {list(df.columns)}")


# ============================================================
# 3. VALIDATE COLUMNS
# ============================================================

required_columns = [
    "comment",
    "language",
    "sentiment"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Missing required column: {column}"
        )


# ============================================================
# 4. CLEAN DATA
# ============================================================

print("\nCleaning dataset...")

df = df.dropna(
    subset=[
        "comment",
        "language",
        "sentiment"
    ]
)

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

# Remove empty comments
df = df[df["comment"] != ""]

# Remove duplicate comments
df = df.drop_duplicates(
    subset=["comment", "language", "sentiment"]
)

# Keep only required languages
allowed_languages = [
    "English",
    "Hindi",
    "Telugu"
]

df = df[
    df["language"].isin(allowed_languages)
]

# Keep only required sentiment labels
allowed_sentiments = [
    "Positive",
    "Negative",
    "Neutral"
]

df = df[
    df["sentiment"].isin(allowed_sentiments)
]

df = df.reset_index(drop=True)

print(f"Cleaned dataset size: {len(df)}")


# ============================================================
# 5. DISPLAY DATA DISTRIBUTION
# ============================================================

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


# ============================================================
# 6. PREPARE FEATURES AND LABELS
# ============================================================

X = df["comment"]

y = df["sentiment"]

language = df["language"]


# ============================================================
# 7. STRATIFIED TRAIN-TEST SPLIT
# ============================================================

print("\nSplitting dataset...")

# Preserve both language and sentiment distribution
stratify_key = (
    df["language"].astype(str)
    + "_"
    + df["sentiment"].astype(str)
)

X_train, X_test, y_train, y_test, language_train, language_test = (
    train_test_split(
        X,
        y,
        language,
        test_size=0.20,
        random_state=42,
        stratify=stratify_key
    )
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")


# ============================================================
# 8. WORD-LEVEL TF-IDF
# ============================================================

print("\nCreating word-level TF-IDF features...")

word_vectorizer = TfidfVectorizer(
    analyzer="word",
    ngram_range=(1, 3),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True,
    max_features=200000
)

X_train_word = word_vectorizer.fit_transform(
    X_train
)

X_test_word = word_vectorizer.transform(
    X_test
)

print(
    "Word feature shape:",
    X_train_word.shape
)


# ============================================================
# 9. CHARACTER-LEVEL TF-IDF
# ============================================================

print("\nCreating character-level TF-IDF features...")

char_vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 6),
    min_df=2,
    sublinear_tf=True,
    max_features=200000
)

X_train_char = char_vectorizer.fit_transform(
    X_train
)

X_test_char = char_vectorizer.transform(
    X_test
)

print(
    "Character feature shape:",
    X_train_char.shape
)


# ============================================================
# 10. COMBINE WORD AND CHARACTER FEATURES
# ============================================================

print("\nCombining TF-IDF features...")

X_train_combined = hstack(
    [
        X_train_word,
        X_train_char
    ]
).tocsr()

X_test_combined = hstack(
    [
        X_test_word,
        X_test_char
    ]
).tocsr()

print(
    "Combined training feature shape:",
    X_train_combined.shape
)

print(
    "Combined testing feature shape:",
    X_test_combined.shape
)


# ============================================================
# 11. TRAIN LOGISTIC REGRESSION WITH GRID SEARCH
# ============================================================

print("\nTraining model...")

base_model = LogisticRegression(
    max_iter=2000,
    solver="lbfgs"
)

param_grid = {
    "C": [
        0.1,
        0.5,
        1.0,
        2.0,
        5.0,
        10.0
    ]
}

grid_search = GridSearchCV(
    estimator=base_model,
    param_grid=param_grid,
    cv=3,
    scoring="accuracy",
    n_jobs=-1,
    verbose=1
)

grid_search.fit(
    X_train_combined,
    y_train
)

model = grid_search.best_estimator_

print("\nTraining completed!")

print(
    "Best parameters:",
    grid_search.best_params_
)

print(
    "Best cross-validation accuracy:",
    round(
        grid_search.best_score_,
        4
    )
)


# ============================================================
# 12. PREDICT TEST DATA
# ============================================================

print("\nEvaluating model...")

y_pred = model.predict(
    X_test_combined
)


# ============================================================
# 13. OVERALL EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

macro_f1 = f1_score(
    y_test,
    y_pred,
    average="macro"
)

weighted_f1 = f1_score(
    y_test,
    y_pred,
    average="weighted"
)

print("\n==============================")
print("OVERALL MODEL PERFORMANCE")
print("==============================")

print(
    f"Accuracy: {accuracy:.4f}"
)

print(
    f"Macro F1 Score: {macro_f1:.4f}"
)

print(
    f"Weighted F1 Score: {weighted_f1:.4f}"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        labels=allowed_sentiments,
        zero_division=0
    )
)


# ============================================================
# 14. CONFUSION MATRIX
# ============================================================

print("\nConfusion Matrix:")

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=allowed_sentiments
)

confusion_df = pd.DataFrame(
    cm,
    index=[
        f"Actual {label}"
        for label in allowed_sentiments
    ],
    columns=[
        f"Predicted {label}"
        for label in allowed_sentiments
    ]
)

print(confusion_df)


# ============================================================
# 15. LANGUAGE-WISE EVALUATION
# ============================================================

print("\n==============================")
print("LANGUAGE-WISE PERFORMANCE")
print("==============================")

evaluation_df = pd.DataFrame(
    {
        "comment": X_test.values,
        "actual": y_test.values,
        "predicted": y_pred,
        "language": language_test.values
    }
)

for lang in allowed_languages:

    language_data = evaluation_df[
        evaluation_df["language"] == lang
    ]

    if len(language_data) == 0:
        continue

    language_accuracy = accuracy_score(
        language_data["actual"],
        language_data["predicted"]
    )

    language_macro_f1 = f1_score(
        language_data["actual"],
        language_data["predicted"],
        average="macro",
        zero_division=0
    )

    print(f"\nLanguage: {lang}")
    print(
        f"Samples: {len(language_data)}"
    )

    print(
        f"Accuracy: {language_accuracy:.4f}"
    )

    print(
        f"Macro F1: {language_macro_f1:.4f}"
    )


# ============================================================
# 16. MISCLASSIFICATION ANALYSIS
# ============================================================

print("\n==============================")
print("MISCLASSIFICATION ANALYSIS")
print("==============================")

misclassified_df = evaluation_df[
    evaluation_df["actual"]
    != evaluation_df["predicted"]
]

print(
    "Total misclassified samples:",
    len(misclassified_df)
)

if len(misclassified_df) > 0:

    print("\nSample misclassified comments:")

    print(
        misclassified_df[
            [
                "comment",
                "language",
                "actual",
                "predicted"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    error_path = os.path.join(
        BASE_DIR,
        "reports",
        "misclassified_comments.csv"
    )

    os.makedirs(
        os.path.dirname(error_path),
        exist_ok=True
    )

    misclassified_df.to_csv(
        error_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"\nMisclassification report saved to: {error_path}"
    )


# ============================================================
# 17. SAVE MODEL
# ============================================================

print("\nSaving model files...")

with open(
    MODEL_PATH,
    "wb"
) as file:

    pickle.dump(
        model,
        file
    )


with open(
    WORD_VECTORIZER_PATH,
    "wb"
) as file:

    pickle.dump(
        word_vectorizer,
        file
    )


with open(
    CHAR_VECTORIZER_PATH,
    "wb"
) as file:

    pickle.dump(
        char_vectorizer,
        file
    )


# ============================================================
# 18. FINAL SUMMARY
# ============================================================

print("\n==============================")
print("TRAINING SUMMARY")
print("==============================")

print(
    f"Dataset size: {len(df)}"
)

print(
    f"Training size: {len(X_train)}"
)

print(
    f"Testing size: {len(X_test)}"
)

print(
    f"Accuracy: {accuracy:.4f}"
)

print(
    f"Macro F1 Score: {macro_f1:.4f}"
)

print(
    f"Best C value: {grid_search.best_params_['C']}"
)

print("\nSaved files:")

print(
    f"- {MODEL_PATH}"
)

print(
    f"- {WORD_VECTORIZER_PATH}"
)

print(
    f"- {CHAR_VECTORIZER_PATH}"
)

print("\nTraining process completed successfully!")