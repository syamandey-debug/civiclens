import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.models import Feedback
from app.services.embedding_service import generate_embedding


def search_similar_feedback(
    db,
    query,
    top_k=3
):
    # Generate embedding for the search query
    query_embedding = generate_embedding(query)

    # Get feedback records that already have embeddings
    feedback_records = (
        db.query(Feedback)
        .filter(Feedback.embedding.is_not(None))
        .all()
    )

    if not feedback_records:
        return []

    # Convert stored embeddings into a NumPy array
    embeddings = np.array(
        [feedback.embedding for feedback in feedback_records]
    )

    # Calculate cosine similarity
    similarities = cosine_similarity(
        [query_embedding],
        embeddings
    )[0]

    # Get indices of highest similarities
    top_indices = np.argsort(
        similarities
    )[::-1][:top_k]

    results = []

    for index in top_indices:

        feedback = feedback_records[index]

        results.append({
            "comment_id": feedback.comment_id,
            "comment": feedback.comment,
            "similarity": float(similarities[index])
        })

    return results