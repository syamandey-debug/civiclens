import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def calculate_similarity(comment_1, comment_2):

    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(
        [comment_1, comment_2],
        normalize_embeddings=True
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return float(similarity)


if __name__ == "__main__":

    comment_1 = (
        "The roads are in very poor condition."
    )

    comment_2 = (
        "The roads need urgent repairs."
    )

    similarity = calculate_similarity(
        comment_1,
        comment_2
    )

    print()
    print("Comment 1:")
    print(comment_1)

    print()
    print("Comment 2:")
    print(comment_2)

    print()
    print(
        f"Semantic similarity: {similarity:.4f}"
    )