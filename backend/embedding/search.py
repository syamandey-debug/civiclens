import pandas as pd
import numpy as np

from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

BASE_DIR = Path(__file__).resolve().parents[2]

FEEDBACK_FILE = BASE_DIR / "data" / "feedback.csv"

EMBEDDINGS_FILE = (
    BASE_DIR / "data" / "feedback_embeddings.npy"
)

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Loading feedback...")

df = pd.read_csv(FEEDBACK_FILE)

print("Loading embeddings...")

embeddings = np.load(EMBEDDINGS_FILE)


def search_similar_feedback(
    query,
    top_k=3
):

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    similarities = cosine_similarity(
        query_embedding,
        embeddings
    )[0]

    top_indices = np.argsort(
        similarities
    )[::-1][:top_k]

    results = []

    for index in top_indices:

        results.append({
            "comment_id": int(
                df.iloc[index]["comment_id"]
            ),
            "comment": df.iloc[index]["comment"],
            "similarity": float(
                similarities[index]
            )
        })

    return results


if __name__ == "__main__":

    query = input(
        "Enter a feedback comment to search: "
    ).strip()

    if not query:

        print("Please enter a comment.")

    else:

        results = search_similar_feedback(
            query,
            top_k=3
        )

        print()
        print("Search query:")
        print(query)

        print()
        print("Similar feedback:")

        for result in results:

            print(
                f"ID: {result['comment_id']} | "
                f"Similarity: "
                f"{result['similarity']:.4f}"
            )

            print(
                f"Comment: {result['comment']}"
            )

            print()