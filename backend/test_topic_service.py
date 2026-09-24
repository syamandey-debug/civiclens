from app.services.topic_classification import classify_topic


comments = [
    "The roads in our area have many potholes.",
    "There has been no water supply for three days.",
    "Garbage has not been collected for a week.",
    "The government hospital does not have enough medicines.",
    "I applied for a birth certificate but my application is still pending.",
]


for comment in comments:
    result = classify_topic(comment)

    print("\nComment:", comment)
    print("Topic:", result["topic"])
    print("Score:", result["score"])