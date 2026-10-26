import pandas as pd
from pathlib import Path

# ==================================================
# CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "student_attempts.csv"
OUTPUT_FILE = BASE_DIR / "data" / "cleaned_student_attempts.csv"

REQUIRED_COLUMNS = [
    "student_id",
    "exercise_id",
    "topic",
    "attempt_number",
    "previous_errors",
    "syntax_error",
    "test_pass_rate",
    "execution_time",
    "error_type",
    "is_correct",
]

VALID_TOPICS = [
    "Variables",
    "Conditional Statements",
    "Loops",
    "Functions",
    "Lists",
    "Strings",
]

VALID_ERROR_TYPES = [
    "Syntax Error",
    "Incorrect Condition",
    "Loop Logic Error",
    "Variable Misuse",
    "Incorrect Output",
    "No Error",
]

NUMERIC_COLUMNS = [
    "attempt_number",
    "previous_errors",
    "syntax_error",
    "test_pass_rate",
    "execution_time",
    "is_correct",
]


# ==================================================
# DATA CLEANING FUNCTION
# ==================================================

def clean_dataset():

    print("\n" + "=" * 60)
    print("             CODEHABIT DATA CLEANING")
    print("=" * 60)

    # 1. Check that the input file exists.
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}\n"
            "Run generate_dataset.py first."
        )

    # 2. Load the dataset.
    df = pd.read_csv(INPUT_FILE)

    print("\n1. ORIGINAL DATASET")
    print("-" * 40)
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    # 3. Check required columns.
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {missing_columns}"
        )

    # Keep only the expected columns in a consistent order.
    df = df[REQUIRED_COLUMNS].copy()

    # 4. Check missing values before cleaning.
    print("\n2. MISSING VALUES BEFORE CLEANING")
    print("-" * 40)

    missing_before = df.isnull().sum()
    print(missing_before.to_string())

    # 5. Remove completely duplicated rows.
    duplicates_before = int(df.duplicated().sum())

    df = df.drop_duplicates().copy()

    print("\n3. DUPLICATE RECORDS")
    print("-" * 40)
    print(f"Duplicate rows found: {duplicates_before}")
    print(f"Duplicate rows removed: {duplicates_before}")

    # 6. Clean text columns.
    text_columns = [
        "student_id",
        "exercise_id",
        "topic",
        "error_type",
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    # Treat blank text as missing.
    for column in text_columns:
        df[column] = df[column].replace("", pd.NA)

    # 7. Convert numeric columns safely.
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # 8. Remove rows missing essential information.
    essential_columns = [
        "student_id",
        "exercise_id",
        "topic",
        "attempt_number",
        "error_type",
        "is_correct",
    ]

    missing_essential = df[essential_columns].isna().any(axis=1)

    removed_missing = int(missing_essential.sum())

    df = df.loc[~missing_essential].copy()

    print("\n4. MISSING ESSENTIAL DATA")
    print("-" * 40)
    print(f"Rows removed: {removed_missing}")

    # 9. Remove invalid categories.
    invalid_topic = ~df["topic"].isin(VALID_TOPICS)
    invalid_error = ~df["error_type"].isin(VALID_ERROR_TYPES)

    invalid_categories = invalid_topic | invalid_error

    removed_categories = int(invalid_categories.sum())

    df = df.loc[~invalid_categories].copy()

    print("\n5. INVALID CATEGORIES")
    print("-" * 40)
    print(f"Rows removed: {removed_categories}")

    # 10. Check numerical values.
    # Values outside reasonable ranges are invalid.

    invalid_numeric = (
        (df["attempt_number"] < 1)
        | (df["attempt_number"] % 1 != 0)
        | (df["previous_errors"] < 0)
        | (df["previous_errors"] % 1 != 0)
        | (~df["syntax_error"].isin([0, 1]))
        | (df["test_pass_rate"] < 0)
        | (df["test_pass_rate"] > 1)
        | (df["execution_time"] < 0)
        | (~df["is_correct"].isin([0, 1]))
    )

    removed_invalid_numeric = int(invalid_numeric.sum())

    df = df.loc[~invalid_numeric].copy()

    print("\n6. INVALID NUMERICAL VALUES")
    print("-" * 40)
    print(f"Rows removed: {removed_invalid_numeric}")

    # 11. Check logical consistency between labels.
    # "No Error" must correspond to is_correct = 1.
    # Other error categories must correspond to is_correct = 0.

    expected_correct = (df["error_type"] == "No Error").astype(int)

    inconsistent_labels = df["is_correct"] != expected_correct

    removed_inconsistent = int(inconsistent_labels.sum())

    df = df.loc[~inconsistent_labels].copy()

    print("\n7. INCONSISTENT LABELS")
    print("-" * 40)
    print(f"Rows removed: {removed_inconsistent}")

    # 12. Convert columns to appropriate data types.
    integer_columns = [
        "attempt_number",
        "previous_errors",
        "syntax_error",
        "is_correct",
    ]

    for column in integer_columns:
        df[column] = df[column].astype(int)

    df["test_pass_rate"] = df["test_pass_rate"].astype(float)
    df["execution_time"] = df["execution_time"].astype(float)

    # 13. Sort rows consistently.
    df = df.sort_values(
        by=["student_id", "attempt_number", "exercise_id"]
    ).reset_index(drop=True)

    # 14. Save the cleaned dataset.
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    # 15. Print final report.
    print("\n8. CLEANING SUMMARY")
    print("-" * 40)
    print(f"Original rows: {len(pd.read_csv(INPUT_FILE))}")
    print(f"Cleaned rows: {len(df)}")
    print(f"Rows remaining: {len(df)}")
    print(f"Rows removed overall: {len(pd.read_csv(INPUT_FILE)) - len(df)}")

    print("\n9. MISSING VALUES AFTER CLEANING")
    print("-" * 40)
    print(df.isnull().sum().to_string())

    print("\n10. ERROR CATEGORY DISTRIBUTION")
    print("-" * 40)
    print(df["error_type"].value_counts().to_string())

    print("\n11. CLEANED DATASET PREVIEW")
    print("-" * 40)
    print(df.head(10).to_string(index=False))

    print("\n" + "=" * 60)
    print("DATA CLEANING COMPLETED SUCCESSFULLY!")
    print(f"Saved cleaned dataset to:\n{OUTPUT_FILE}")
    print("=" * 60)


# ==================================================
# PROGRAM ENTRY POINT
# ==================================================

if __name__ == "__main__":
    clean_dataset()
