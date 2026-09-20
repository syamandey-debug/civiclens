import os
import pickle
import warnings

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

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "training_data.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


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

print("\nLoading English dataset...")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}\n"
        "Run prepare_dataset.py first."
    )

df = pd.read_csv(DATA_PATH)

print(
    f"Original dataset size: {len(df)}"
)


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
# 4. KEEP ENGLISH ONLY
# ============================================================

print("\nKeeping English comments only...")

df = df[
    df["language"].astype(str).str.strip()
    == "English"
].copy()


# ============================================================
# 5. CLEAN DATA
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
df = df[
    df["comment"] != ""
]

# Keep supported sentiment labels
allowed_sentiments = [
    "Positive",
    "Negative",
    "Neutral"
]

df = df[
    df["sentiment"].isin(
        allowed_sentiments
    )
]

# Remove duplicate comments
df = df.drop_duplicates(
    subset=[
        "comment",
        "sentiment"
    ]
)

df = df.reset_index(
    drop=True
)

if len(df) == 0:

    raise ValueError(
        "No English data available. "
        "Check training_data.csv."
    )

print(
    f"English dataset size: {len(df)}"
)


# ============================================================
# 6. DISPLAY DATA DISTRIBUTION
# ============================================================

print("\nLanguage distribution:")

print(
    df["language"].value_counts()
)

print("\nSentiment distribution:")

print(
    df["sentiment"].value_counts()
)


# ============================================================
# 7. PREPARE FEATURES AND LABELS
# ============================================================

X = df["comment"]

y = df["sentiment"]


# ============================================================
# 8. STRATIFIED TRAIN-TEST SPLIT
# ============================================================

print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
)

print(
    f"Training samples: {len(X_train)}"
)

print(
    f"Testing samples: {len(X_test)}"
)


# ============================================================
# 9. WORD-LEVEL TF-IDF
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

X_train_word = (
    word_vectorizer.fit_transform(
        X_train
    )
)

X_test_word = (
    word_vectorizer.transform(
        X_test
    )
)

print(
    "Word feature shape:",
    X_train_word.shape
)


# ============================================================
# 10. CHARACTER-LEVEL TF-IDF
# ============================================================

print("\nCreating character-level TF-IDF features...")

char_vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 6),
    min_df=2,
    sublinear_tf=True,
    max_features=200000
)

X_train_char = (
    char_vectorizer.fit_transform(
        X_train
    )
)

X_test_char = (
    char_vectorizer.transform(
        X_test
    )
)

print(
    "Character feature shape:",
    X_train_char.shape
)


# ============================================================
# 11. COMBINE FEATURES
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
# 12. TRAIN LOGISTIC REGRESSION
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
    "Best CV accuracy:",
    round(
        grid_search.best_score_,
        4
    )
)


# ============================================================
# 13. PREDICTIONS
# ============================================================

print("\nEvaluating model...")

y_pred = model.predict(
    X_test_combined
)


# ============================================================
# 14. OVERALL EVALUATION
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

print("\n========================================")
print("ENGLISH MODEL PERFORMANCE")
print("========================================")

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
# 15. CONFUSION MATRIX
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
# 16. MISCLASSIFICATION ANALYSIS
# ============================================================

print("\n========================================")
print("MISCLASSIFICATION ANALYSIS")
print("========================================")

evaluation_df = pd.DataFrame(
    {
        "comment": X_test.values,
        "actual": y_test.values,
        "predicted": y_pred
    }
)

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
        misclassified_df
        .head(20)
        .to_string(index=False)
    )

    error_path = os.path.join(
        REPORT_DIR,
        "misclassified_comments.csv"
    )

    misclassified_df.to_csv(
        error_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        "\nMisclassification report saved:"
    )

    print(error_path)


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

print("\n========================================")
print("TRAINING SUMMARY")
print("========================================")

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

print("\nEnglish-only training completed successfully!")