import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.models import Feedback
from app.services.embedding_service import generate_embedding


def search_similar_feedback(
    db,
    query,
    top_k=3,
    threshold=0.50
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

    # Sort all records from highest similarity to lowest
    sorted_indices = np.argsort(
        similarities
    )[::-1]

    results = []
    seen_comments = set()

    for index in sorted_indices:

        # Ignore weak matches
        if similarities[index] < threshold:
            break

        feedback = feedback_records[index]

        # Skip exact duplicate comments
        if feedback.comment in seen_comments:
            continue

        seen_comments.add(feedback.comment)

        results.append({
            "comment_id": feedback.comment_id,
            "comment": feedback.comment,
            "similarity": float(similarities[index])
        })

        # Stop after top_k unique results
        if len(results) == top_k:
            break

    return {
    "query": query,
    "results": results,
    "message": (
        "No sufficiently similar feedback found."
        if not results
        else "Similar records found."
    )
    }