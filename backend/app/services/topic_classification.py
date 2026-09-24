from transformers import pipeline


# --------------------------------------------------
# Load zero-shot classification model
# --------------------------------------------------

topic_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)


# --------------------------------------------------
# CivicLens topic categories
# --------------------------------------------------

TOPICS = [
    "Roads and Infrastructure",
    "Water Supply",
    "Sanitation and Waste Management",
    "Public Transportation",
    "Electricity and Power Supply",
    "Healthcare Services",
    "Education Services",
    "Public Safety and Street Lighting",
    "Government Services",
    "Environment and Parks"
]


# --------------------------------------------------
# Topic classification
# --------------------------------------------------

def classify_topic(comment: str):
    """
    Classify a feedback comment into one of the
    predefined CivicLens topics.
    """

    if not comment or not comment.strip():
        return {
            "topic": None,
            "score": 0.0
        }

    result = topic_classifier(
        comment.strip(),
        candidate_labels=TOPICS,
        hypothesis_template="This feedback is about {}."
    )

    return {
        "topic": result["labels"][0],
        "score": round(float(result["scores"][0]), 4)
    }