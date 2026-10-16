
import sqlite3

conn = sqlite3.connect("civiclens.db")
cursor = conn.cursor()

# Check whether the column exists
columns = [
    column[1]
    for column in cursor.execute(
        'PRAGMA table_info("feedback")'
    ).fetchall()
]

print("cluster_id column exists:", "cluster_id" in columns)

if "cluster_id" in columns:
    # Count records with and without cluster assignments
    print("\nCluster assignments:")
    rows = cursor.execute("""
        SELECT cluster_id, COUNT(*)
        FROM feedback
        GROUP BY cluster_id
        ORDER BY cluster_id
    """).fetchall()

    for cluster_id, count in rows:
        print(f"Cluster {cluster_id}: {count} records")

    total = cursor.execute(
        "SELECT COUNT(*) FROM feedback"
    ).fetchone()[0]

    assigned = cursor.execute("""
        SELECT COUNT(*)
        FROM feedback
        WHERE cluster_id IS NOT NULL
    """).fetchone()[0]

    print("\nTotal records:", total)
    print("Records assigned to clusters:", assigned)
    print("Records without cluster assignment:", total - assigned)

conn.close()
