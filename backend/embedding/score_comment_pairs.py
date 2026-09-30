import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

INPUT_FILE = (
    "../../data/embedding_comment_pairs(2).csv"
)

OUTPUT_FILE = (
    "../../data/embedding_comment_pairs_scored.csv"
)


print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Embedding model loaded.")


print("Loading comment pairs...")

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df)} comment pairs.")


required_columns = [
    "comment_1",
    "comment_2"
]

for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Missing required column: {column}"
        )


comments_1 = (
    df["comment_1"]
    .fillna("")
    .astype(str)
    .str.strip()
)

comments_2 = (
    df["comment_2"]
    .fillna("")
    .astype(str)
    .str.strip()
)


print("Generating embeddings for comment 1...")

embeddings_1 = model.encode(
    comments_1.tolist(),
    normalize_embeddings=True,
    show_progress_bar=True
)


print("Generating embeddings for comment 2...")

embeddings_2 = model.encode(
    comments_2.tolist(),
    normalize_embeddings=True,
    show_progress_bar=True
)


print("Calculating similarity scores...")

similarities = []

for embedding_1, embedding_2 in zip(
    embeddings_1,
    embeddings_2
):

    score = cosine_similarity(
        [embedding_1],
        [embedding_2]
    )[0][0]

    similarities.append(float(score))


df["embedding_similarity"] = similarities


df.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("Similarity scoring completed!")
print(
    f"Saved scored dataset to: {OUTPUT_FILE}"
)

print()
print("First 5 similarity scores:")

print(
    df[
        [
            "comment_1",
            "comment_2",
            "embedding_similarity"
        ]
    ].head()
)