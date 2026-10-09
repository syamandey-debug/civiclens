
import numpy as np
from sklearn.cluster import DBSCAN

from app.models import Feedback


def cluster_feedback(
    db,
    eps=0.25,
    min_samples=2
):
    # Get feedback records that already have embeddings
    feedback_records = (
        db.query(Feedback)
        .filter(Feedback.embedding.is_not(None))
        .all()
    )

    if not feedback_records:
        return {
            "message": "No feedback embeddings found.",
            "clusters": {}
        }

    # Reuse existing embeddings; do not generate them again
    embeddings = np.array(
        [feedback.embedding for feedback in feedback_records],
        dtype=float
    )

    # Cluster using cosine distance
    model = DBSCAN(
        eps=eps,
        min_samples=min_samples,
        metric="cosine"
    )

    labels = model.fit_predict(embeddings)

    clusters = {}
    updated_count = 0

    for feedback, label in zip(feedback_records, labels):

        # DBSCAN label -1 means noise
        feedback.cluster_id = (
            int(label) if label != -1 else None
        )

        if label != -1:
            clusters.setdefault(int(label), []).append({
                "comment_id": feedback.comment_id,
                "comment": feedback.comment,
                "topic": feedback.predicted_topic,
                "sentiment": feedback.predicted_sentiment
            })

        updated_count += 1

    db.commit()

    return {
        "message": "Semantic clustering completed.",
        "records_processed": updated_count,
        "cluster_count": len(clusters),
        "noise_count": int(np.sum(labels == -1)),
        "clusters": clusters
    }
