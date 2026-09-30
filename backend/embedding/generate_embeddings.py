import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. Model configuration
# --------------------------------------------------

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "feedback.csv"

OUTPUT_FILE = BASE_DIR / "data" / "feedback_embeddings.npy"

# --------------------------------------------------
# 3. Load the embedding model
# --------------------------------------------------

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Embedding model loaded successfully.")


# --------------------------------------------------
# 4. Load the feedback dataset
# --------------------------------------------------

print("Loading feedback dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df)} feedback records.")


# --------------------------------------------------
# 5. Check that the comment column exists
# --------------------------------------------------

if "comment" not in df.columns:

    raise ValueError(
        "Dataset must contain a 'comment' column."
    )


# --------------------------------------------------
# 6. Clean the comments
# --------------------------------------------------

comments = (
    df["comment"]
    .fillna("")
    .astype(str)
    .str.strip()
)

print("Comments prepared for embedding.")


# --------------------------------------------------
# 7. Generate embeddings
# --------------------------------------------------

print("Generating embeddings...")

embeddings = model.encode(
    comments.tolist(),
    show_progress_bar=True,
    normalize_embeddings=True
)

embeddings = np.asarray(embeddings)


# --------------------------------------------------
# 8. Save embeddings
# --------------------------------------------------

np.save(
    OUTPUT_FILE,
    embeddings
)


# --------------------------------------------------
# 9. Display information
# --------------------------------------------------

print()
print("Embedding generation completed!")
print(f"Embeddings saved to: {OUTPUT_FILE}")
print(f"Embedding shape: {embeddings.shape}")