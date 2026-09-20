import os
import pickle

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
# 2. LOAD MODEL FILES
# ============================================================

def load_model_files():

    print("\nLoading English model files...")

    required_files = [
        MODEL_PATH,
        WORD_VECTORIZER_PATH,
        CHAR_VECTORIZER_PATH
    ]

    for file_path in required_files:

        if not os.path.exists(file_path):

            raise FileNotFoundError(
                f"File not found: {file_path}\n"
                "Please run train_model.py first."
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

    print("English model files loaded successfully!")

    print(
        "Model classes:",
        list(model.classes_)
    )

    return (
        model,
        word_vectorizer,
        char_vectorizer
    )


# ============================================================
# 3. PREDICT SENTIMENT
# ============================================================

def predict_sentiment(
    comment,
    model,
    word_vectorizer,
    char_vectorizer
):

    if not isinstance(comment, str) or not comment.strip():

        return {
            "sentiment": "Invalid input",
            "probability": 0.0,
            "probabilities": {}
        }

    comment = comment.strip()

    # Word-level features
    word_features = word_vectorizer.transform(
        [comment]
    )

    # Character-level features
    char_features = char_vectorizer.transform(
        [comment]
    )

    # Combine features
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

    # Calculate probability estimates
    probabilities = model.predict_proba(
        combined_features
    )[0]

    # Find probability of predicted class
    class_probabilities = dict(
        zip(
            model.classes_,
            probabilities
        )
    )

    prediction_probability = class_probabilities[
        prediction
    ]

    return {
        "sentiment": prediction,
        "probability": prediction_probability,
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
        f"Predicted Sentiment: "
        f"{result['sentiment']}"
    )

    if result["sentiment"] != "Invalid input":

        print(
            f"Prediction Probability: "
            f"{result['probability'] * 100:.2f}%"
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
# 5. SAMPLE ENGLISH COMMENTS
# ============================================================

def run_sample_tests(
    model,
    word_vectorizer,
    char_vectorizer
):

    test_comments = [

        "The road repair work was successfully completed.",

        "The garbage collection service is very poor.",

        "The government announced a new transport project.",

        "The streetlights are not working.",

        "The water supply has improved.",

        "The public hospital provides excellent service.",

        "The roads are full of potholes.",

        "The municipality has improved waste management.",

        "The water supply is irregular and unreliable.",

        "The new public park is clean and well maintained.",

        "The drainage system is completely blocked.",

        "The city has introduced a new bus service."

    ]

    print("\n========================================")

    print("ENGLISH SENTIMENT PREDICTIONS")

    print("========================================")

    for comment in test_comments:

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
# 6. INTERACTIVE TESTING
# ============================================================

def interactive_testing(

    model,

    word_vectorizer,

    char_vectorizer

):

    print("\n========================================")

    print("INTERACTIVE ENGLISH TESTING")

    print("========================================")

    print(

        "Enter an English comment."

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

                "\nDo you want to test your own English comment? "

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