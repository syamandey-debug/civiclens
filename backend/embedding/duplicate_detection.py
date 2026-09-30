import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# FILE PATHS
# =========================

BASE_DIR = Path(__file__).resolve().parents[2]

FEEDBACK_FILE = BASE_DIR / "data" / "feedback.csv"

EMBEDDINGS_FILE = (
    BASE_DIR / "data" / "feedback_embeddings.npy"
)


# =========================
# LOAD DATA
# =========================

def load_feedback_data():

    print("Loading feedback...")
    df = pd.read_csv(FEEDBACK_FILE)

    print("Loading embeddings...")
    embeddings = np.load(EMBEDDINGS_FILE)

    if len(df) != len(embeddings):

        raise ValueError(
            "Number of feedback records does not "
            "match number of embeddings."
        )

    return df, embeddings


# =========================
# FIND DUPLICATES
# =========================

def find_near_duplicates(
    threshold=0.80
):

    df, embeddings = load_feedback_data()

    similarity_matrix = cosine_similarity(
        embeddings
    )

    duplicates = []

    for i in range(len(df)):

        for j in range(i + 1, len(df)):

            similarity = similarity_matrix[i][j]

            if similarity >= threshold:

                duplicates.append(
                    {
                        "comment_id_1": int(
                            df.iloc[i]["comment_id"]
                        ),

                        "comment_1": str(
                            df.iloc[i]["comment"]
                        ),

                        "comment_id_2": int(
                            df.iloc[j]["comment_id"]
                        ),

                        "comment_2": str(
                            df.iloc[j]["comment"]
                        ),

                        "similarity": float(
                            similarity
                        )
                    }
                )

    duplicates.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return duplicates


# =========================
# TEST
# =========================

if __name__ == "__main__":

    print("Checking for near-duplicate feedback...")

    results = find_near_duplicates(
        threshold=0.80
    )

    print()
    print(
        f"Found {len(results)} "
        "possible near-duplicate pairs."
    )

    for result in results:

        print()
        print(
            f"Feedback "
            f"{result['comment_id_1']} "
            f"<-> "
            f"{result['comment_id_2']}"
        )

        print(
            f"Similarity: "
            f"{result['similarity']:.4f}"
        )

        print(
            f"Comment 1: "
            f"{result['comment_1']}"
        )

        print(
            f"Comment 2: "
            f"{result['comment_2']}"
        )