import os
import pickle

import pandas as pd
from scipy.sparse import hstack


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "sentiment_model.pkl"
)

WORD_VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "word_vectorizer.pkl"
)

CHAR_VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "char_vectorizer.pkl"
)


# ============================================================
# 2. LOAD MODEL AND VECTORIZERS
# ============================================================

def load_model_files():

    print("\nLoading model files...")

    required_files = [
        MODEL_PATH,
        WORD_VECTORIZER_PATH,
        CHAR_VECTORIZER_PATH
    ]

    for file_path in required_files:

        if not os.path.exists(file_path):

            raise FileNotFoundError(
                f"File not found: {file_path}\n"
                "Please train the model first."
            )

    with open(
        MODEL_PATH,
        "rb"
    ) as file:

        model = pickle.load(file)

    with open(
        WORD_VECTORIZER_PATH,
        "rb"
    ) as file:

        word_vectorizer = pickle.load(file)

    with open(
        CHAR_VECTORIZER_PATH,
        "rb"
    ) as file:

        char_vectorizer = pickle.load(file)

    print("Model files loaded successfully!")

    return (
        model,
        word_vectorizer,
        char_vectorizer
    )


# ============================================================
# 3. PREDICTION FUNCTION
# ============================================================

def predict_sentiment(
    comment,
    model,
    word_vectorizer,
    char_vectorizer
):

    if not comment or not comment.strip():

        return {
            "sentiment": "Invalid input",
            "confidence": 0.0
        }

    comment = comment.strip()

    # Convert comment into word features
    word_features = word_vectorizer.transform(
        [comment]
    )

    # Convert comment into character features
    char_features = char_vectorizer.transform(
        [comment]
    )

    # Combine both feature types
    combined_features = hstack(
        [
            word_features,
            char_features
        ]
    ).tocsr()

    # Predict sentiment
    prediction = model.predict(
        combined_features
    )[0]

    # Calculate probability estimate
    probabilities = model.predict_proba(
        combined_features
    )[0]

    # Get the highest probability
    confidence = max(probabilities)

    # Get all class probabilities
    class_probabilities = dict(
        zip(
            model.classes_,
            probabilities
        )
    )

    return {
        "sentiment": prediction,
        "confidence": confidence,
        "probabilities": class_probabilities
    }


# ============================================================
# 4. DISPLAY PREDICTION
# ============================================================

def display_prediction(
    comment,
    result
):

    print("\n----------------------------------------")

    print(
        f"Comment: {comment}"
    )

    print(
        f"Predicted Sentiment: {result['sentiment']}"
    )

    if result["sentiment"] != "Invalid input":

        print(
            f"Probability Estimate: "
            f"{result['confidence'] * 100:.2f}%"
        )

        print("\nClass probabilities:")

        for sentiment, probability in (
            result["probabilities"].items()
        ):

            print(
                f"  {sentiment}: "
                f"{probability * 100:.2f}%"
            )

    print("----------------------------------------")


# ============================================================
# 5. PREDEFINED TEST COMMENTS
# ============================================================

def run_sample_tests(
    model,
    word_vectorizer,
    char_vectorizer
):

    test_comments = [

        {
            "language": "English",
            "comment": (
                "The road repair work was "
                "successfully completed."
            )
        },

        {
            "language": "English",
            "comment": (
                "The garbage collection service "
                "is very poor."
            )
        },

        {
            "language": "English",
            "comment": (
                "The government announced "
                "a new transport project."
            )
        },

        {
            "language": "English",
            "comment": (
                "The streetlights are not working."
            )
        },

        {
            "language": "English",
            "comment": (
                "The water supply has improved."
            )
        },

        {
            "language": "Hindi",
            "comment": (
                "सड़क की मरम्मत का काम "
                "सफलतापूर्वक पूरा हो गया है।"
            )
        },

        {
            "language": "Hindi",
            "comment": (
                "कचरा संग्रहण सेवा बहुत खराब है।"
            )
        },

        {
            "language": "Hindi",
            "comment": (
                "सड़क की लाइटें काम नहीं कर रही हैं।"
            )
        },

        {
            "language": "Telugu",
            "comment": (
                "రోడ్డు మరమ్మతు పనులు "
                "విజయవంతంగా పూర్తయ్యాయి."
            )
        },

        {
            "language": "Telugu",
            "comment": (
                "చెత్త సేకరణ సేవ చాలా అధ్వాన్నంగా ఉంది."
            )
        },

        {
            "language": "Telugu",
            "comment": (
                "వీధి దీపాలు పనిచేయడం లేదు."
            )
        },

        {
            "language": "Telugu",
            "comment": (
                "నీటి సరఫరా మెరుగుపడింది."
            )
        }

    ]

    print("\n========================================")
    print("SAMPLE SENTIMENT PREDICTIONS")
    print("========================================")

    for item in test_comments:

        print(
            f"\nLanguage: {item['language']}"
        )

        result = predict_sentiment(
            item["comment"],
            model,
            word_vectorizer,
            char_vectorizer
        )

        display_prediction(
            item["comment"],
            result
        )


# ============================================================
# 6. INTERACTIVE TESTING
# ============================================================

def interactive_testing(
    model,
    word_vectorizer,
    char_vectorizer
):

    print("\n========================================")
    print("INTERACTIVE SENTIMENT TESTING")
    print("========================================")

    print(
        "Enter a comment in English, Hindi, or Telugu."
    )

    print(
        "Type 'exit' to stop."
    )

    while True:

        comment = input(
            "\nEnter your comment: "
        ).strip()

        if comment.lower() == "exit":

            print(
                "\nExiting interactive testing."
            )

            break

        if not comment:

            print(
                "Please enter a valid comment."
            )

            continue

        result = predict_sentiment(
            comment,
            model,
            word_vectorizer,
            char_vectorizer
        )

        display_prediction(
            comment,
            result
        )


# ============================================================
# 7. MAIN FUNCTION
# ============================================================

def main():

    try:

        (
            model,
            word_vectorizer,
            char_vectorizer
        ) = load_model_files()

        run_sample_tests(
            model,
            word_vectorizer,
            char_vectorizer
        )

        while True:

            choice = input(
                "\nDo you want to test your own comment? "
                "(yes/no): "
            ).strip().lower()

            if choice in [
                "yes",
                "y"
            ]:

                interactive_testing(
                    model,
                    word_vectorizer,
                    char_vectorizer
                )

                break

            elif choice in [
                "no",
                "n"
            ]:

                print(
                    "\nTesting completed."
                )

                break

            else:

                print(
                    "Please enter yes or no."
                )

    except FileNotFoundError as error:

        print(
            f"\nERROR: {error}"
        )

    except Exception as error:

        print(
            "\nAn unexpected error occurred:"
        )

        print(error)


# ============================================================
# 8. PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()