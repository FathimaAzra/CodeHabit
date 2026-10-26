from pathlib import Path

import joblib
import pandas as pd


# ==================================================
# CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_FILE = BASE_DIR / "outputs" / "codehabit_model.joblib"


# ==================================================
# RECOMMENDATIONS
# ==================================================

RECOMMENDATIONS = {
    "Syntax Error": {
        "title": "Review Python Syntax",
        "message": (
            "Check indentation, colons, brackets, quotation marks, "
            "and spelling of Python keywords."
        ),
        "practice": (
            "Practise writing simple Python statements and functions."
        ),
    },

    "Incorrect Condition": {
        "title": "Practise Conditional Statements",
        "message": (
            "Review if, elif, and else statements. "
            "Check comparison operators and logical conditions."
        ),
        "practice": (
            "Solve exercises involving even numbers, ranges, "
            "and multiple conditions."
        ),
    },

    "Loop Logic Error": {
        "title": "Review Loop Logic",
        "message": (
            "Check loop conditions, iteration ranges, "
            "and whether your loop terminates correctly."
        ),
        "practice": (
            "Practise counting loops, summation, and number patterns."
        ),
    },

    "Variable Misuse": {
        "title": "Practise Variable Usage",
        "message": (
            "Check variable names, assignments, initial values, "
            "and whether variables are used consistently."
        ),
        "practice": (
            "Practise storing, updating, and printing variable values."
        ),
    },

    "Incorrect Output": {
        "title": "Review Program Output",
        "message": (
            "Check the expected result, calculation steps, "
            "return values, and output formatting."
        ),
        "practice": (
            "Trace your program manually and compare its output "
            "with the expected result."
        ),
    },

    "No Error": {
        "title": "Good Progress!",
        "message": (
            "The model predicts that this attempt belongs "
            "to the No Error category."
        ),
        "practice": (
            "Try a more challenging exercise and continue practising."
        ),
    },
}


# ==================================================
# LOAD THE SAVED MODEL
# ==================================================

def load_model():

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_FILE}\n"
            "Train the model first using:\n"
            "python ml\\train_model.py"
        )

    # Only load model files that you generated and trust.
    model_bundle = joblib.load(MODEL_FILE)

    if not isinstance(model_bundle, dict):
        raise ValueError(
            "Unexpected model file format. "
            "Please retrain the model."
        )

    if "model" not in model_bundle:
        raise ValueError(
            "The saved model bundle does not contain a model."
        )

    return model_bundle


# ==================================================
# PREDICT AN ERROR CATEGORY
# ==================================================

def predict_error(
    topic,
    attempt_number,
    previous_errors,
    syntax_error,
    test_pass_rate,
    execution_time,
):
    """
    Predict an error category using attempt-level features.

    Note:
    This function predicts a category from supplied features.
    It does not inspect or execute source code.
    """

    model_bundle = load_model()

    model = model_bundle["model"]

    feature_columns = model_bundle["feature_columns"]

    # Validate inputs.
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Topic must be a non-empty string.")

    if isinstance(attempt_number, bool) or not isinstance(
        attempt_number, int
    ):
        raise ValueError("Attempt number must be an integer.")

    if isinstance(previous_errors, bool) or not isinstance(
        previous_errors, int
    ):
        raise ValueError("Previous errors must be an integer.")

    if syntax_error not in (0, 1):
        raise ValueError("syntax_error must be 0 or 1.")

    if not 0 <= test_pass_rate <= 1:
        raise ValueError(
            "Test pass rate must be between 0 and 1."
        )

    if execution_time < 0:
        raise ValueError(
            "Execution time cannot be negative."
        )

    if attempt_number < 1:
        raise ValueError(
            "Attempt number must be at least 1."
        )

    if previous_errors < 0:
        raise ValueError(
            "Previous errors cannot be negative."
        )

    # Create a single-row DataFrame using the exact
    # feature names expected during model training.
    input_data = pd.DataFrame(
        [
            {
                "topic": topic.strip(),
                "attempt_number": attempt_number,
                "previous_errors": previous_errors,
                "syntax_error": int(syntax_error),
                "test_pass_rate": float(test_pass_rate),
                "execution_time": float(execution_time),
            }
        ],
        columns=feature_columns,
    )

    # Predict the error category.
    predicted_category = str(
        model.predict(input_data)[0]
    )

    # Get model probabilities, if supported.
    confidence = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_data)[0]

        confidence = round(
            float(max(probabilities)),
            4,
        )

    recommendation = RECOMMENDATIONS.get(
        predicted_category,
        {
            "title": "Review Your Code",
            "message": (
                "Review the program logic and test the code "
                "against the expected output."
            ),
            "practice": (
                "Try a smaller example and trace each step."
            ),
        },
    )

    return {
        "predicted_error": predicted_category,
        "confidence": confidence,
        "recommendation": recommendation,
        "dataset_type": model_bundle.get(
            "dataset_type",
            "unknown",
        ),
        "warning": (
            "This is an ML prediction based on attempt features. "
            "It is not a verified diagnosis of the submitted code. "
            "The current model was trained on synthetic data."
        ),
    }


# ==================================================
# TEST THE PREDICTION SYSTEM
# ==================================================

if __name__ == "__main__":

    sample = {
        "topic": "Conditional Statements",
        "attempt_number": 2,
        "previous_errors": 4,
        "syntax_error": 0,
        "test_pass_rate": 0.40,
        "execution_time": 0.25,
    }

    print("\n" + "=" * 55)
    print("          CODEHABIT PREDICTION TEST")
    print("=" * 55)

    print("\nInput features:")

    for key, value in sample.items():
        print(f"{key}: {value}")

    result = predict_error(**sample)

    print("\nPrediction result:")
    print("-" * 55)
    print(f"Predicted category: {result['predicted_error']}")

    if result["confidence"] is not None:
        print(
            "Model confidence: "
            f"{result['confidence']:.2%}"
        )

    print(
        f"\nRecommendation: "
        f"{result['recommendation']['title']}"
    )

    print(
        f"Explanation: "
        f"{result['recommendation']['message']}"
    )

    print(
        f"Practice suggestion: "
        f"{result['recommendation']['practice']}"
    )

    print(f"\nWarning: {result['warning']}")

    print("\n" + "=" * 55)

