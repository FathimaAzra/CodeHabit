import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier


# ==================================================
# CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "cleaned_student_attempts.csv"

OUTPUT_DIR = BASE_DIR / "outputs"

MODEL_FILE = OUTPUT_DIR / "codehabit_model.joblib"

METRICS_FILE = OUTPUT_DIR / "model_metrics.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# FEATURES AND TARGET
# ==================================================

FEATURE_COLUMNS = [
    "topic",
    "attempt_number",
    "previous_errors",
    "syntax_error",
    "test_pass_rate",
    "execution_time",
]

TARGET_COLUMN = "error_type"

GROUP_COLUMN = "student_id"

NUMERIC_FEATURES = [
    "attempt_number",
    "previous_errors",
    "syntax_error",
    "test_pass_rate",
    "execution_time",
]

CATEGORICAL_FEATURES = [
    "topic",
]


# ==================================================
# LOAD DATA
# ==================================================

def load_dataset():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {DATA_FILE}\n"
            "Run python ml\\clean_data.py first."
        )

    df = pd.read_csv(DATA_FILE)

    if len(df) < 20:
        raise ValueError(
            "The dataset is too small for this demonstration."
        )

    required_columns = (
        FEATURE_COLUMNS
        + [TARGET_COLUMN, GROUP_COLUMN]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df = df.dropna(
        subset=required_columns
    ).copy()

    if df[TARGET_COLUMN].nunique() < 2:
        raise ValueError(
            "The target must contain at least two error categories."
        )

    print("\n" + "=" * 60)
    print("          CODEHABIT MODEL TRAINING")
    print("=" * 60)

    print(f"\nTotal usable records: {len(df)}")

    print("\nTarget category distribution:")
    print(df[TARGET_COLUMN].value_counts().to_string())

    return df


# ==================================================
# SPLIT DATA BY STUDENT
# ==================================================

def split_dataset(df):

    # Attempts from one student stay together in either
    # training or testing data.
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.25,
        random_state=42,
    )

    train_indices, test_indices = next(
        splitter.split(
            df[FEATURE_COLUMNS],
            df[TARGET_COLUMN],
            groups=df[GROUP_COLUMN],
        )
    )

    train_df = df.iloc[train_indices].copy()
    test_df = df.iloc[test_indices].copy()

    train_students = set(train_df[GROUP_COLUMN])
    test_students = set(test_df[GROUP_COLUMN])

    if train_students.intersection(test_students):
        raise RuntimeError(
            "Student leakage detected between training and testing."
        )

    if train_df[TARGET_COLUMN].nunique() < 2:
        raise ValueError(
            "Training data contains fewer than two target categories. "
            "Regenerate the dataset or adjust the split."
        )

    print("\nDATA SPLIT")
    print("-" * 40)

    print(f"Training records: {len(train_df)}")
    print(f"Testing records: {len(test_df)}")
    print(f"Training students: {len(train_students)}")
    print(f"Testing students: {len(test_students)}")

    print("Student overlap: 0")

    return train_df, test_df


# ==================================================
# BUILD THE MODEL
# ==================================================

def build_model():

    # Convert text categories into numerical features.
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "topic",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                CATEGORICAL_FEATURES,
            ),
            (
                "numeric",
                "passthrough",
                NUMERIC_FEATURES,
            ),
        ]
    )

    classifier = DecisionTreeClassifier(
        max_depth=6,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )

    return model


# ==================================================
# TRAIN AND EVALUATE
# ==================================================

def train_and_evaluate():

    df = load_dataset()

    train_df, test_df = split_dataset(df)

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]

    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    model = build_model()

    print("\nTraining the model...")

    model.fit(X_train, y_train)

    # Predict categories for held-out students.
    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    labels = sorted(
        df[TARGET_COLUMN].unique().tolist()
    )

    report = classification_report(
        y_test,
        predictions,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )

    report_text = classification_report(
        y_test,
        predictions,
        labels=labels,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=labels,
    )

    print("\nMODEL EVALUATION")
    print("=" * 60)

    print(f"Test accuracy: {accuracy:.4f}")
    print(f"Test accuracy percentage: {accuracy * 100:.2f}%")

    print("\nClassification report:")
    print(report_text)

    print("\nConfusion matrix:")
    print("Class order:", labels)
    print(matrix)

    # Save the model and the metadata required by the API.
    model_bundle = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "class_labels": labels,
        "dataset_type": "synthetic",
        "random_state": 42,
    }

    joblib.dump(
        model_bundle,
        MODEL_FILE,
    )

    # Save evaluation metrics for project reporting.
    metrics = {
        "dataset_type": "synthetic",
        "total_records": int(len(df)),
        "training_records": int(len(train_df)),
        "testing_records": int(len(test_df)),
        "training_students": int(
            train_df[GROUP_COLUMN].nunique()
        ),
        "testing_students": int(
            test_df[GROUP_COLUMN].nunique()
        ),
        "student_overlap": 0,
        "accuracy": float(accuracy),
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
        "class_labels": labels,
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "model": "DecisionTreeClassifier",
    }

    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )

    print("\n" + "=" * 60)
    print("MODEL TRAINING COMPLETED!")
    print("=" * 60)

    print(f"Saved model: {MODEL_FILE}")
    print(f"Saved evaluation metrics: {METRICS_FILE}")

    print(
        "\nNote: This evaluation uses synthetic data. "
        "It does not establish real-world predictive accuracy."
    )


# ==================================================
# PROGRAM ENTRY POINT
# ==================================================

if __name__ == "__main__":
    train_and_evaluate()

