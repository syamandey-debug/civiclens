
from app.database import SessionLocal
from app.services.semantic_clustering import cluster_feedback

db = SessionLocal()

try:
    result = cluster_feedback(
    db,
    eps=0.25,
    min_samples=2
    )

    print("Message:", result["message"])
    print("Records processed:", result.get("records_processed", 0))
    print("Clusters found:", result.get("cluster_count", 0))
    print("Noise records:", result.get("noise_count", 0))

    for cluster_id, comments in result.get("clusters", {}).items():
        print(f"\nCluster {cluster_id}")

        for item in comments:
            print(
                item["comment_id"],
                item["comment"]
            )

finally:
    db.close()
