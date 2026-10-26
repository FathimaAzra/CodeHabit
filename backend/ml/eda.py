import pandas as pd
import matplotlib

# Use a non-interactive backend so charts can be saved
# without requiring a separate plotting window.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path


# ==================================================
# CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "cleaned_student_attempts.csv"
OUTPUT_DIR = BASE_DIR / "outputs" / "eda"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# LOAD DATA
# ==================================================

def load_data():
    """Load the cleaned CodeHabit dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {DATA_FILE}\n"
            "Run python ml\\clean_data.py first."
        )

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        raise ValueError("The cleaned dataset is empty.")

    print("\n" + "=" * 60)
    print("       CODEHABIT EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    print("\nDATASET OVERVIEW")
    print("-" * 40)
    print(f"Total records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Unique students: {df['student_id'].nunique()}")
    print(f"Unique exercises: {df['exercise_id'].nunique()}")
    print(f"Unique topics: {df['topic'].nunique()}")

    print("\nDATA TYPES")
    print("-" * 40)
    print(df.dtypes.to_string())

    print("\nMISSING VALUES")
    print("-" * 40)
    print(df.isnull().sum().to_string())

    return df


# ==================================================
# 1. ERROR CATEGORY DISTRIBUTION
# ==================================================

def plot_error_distribution(df):

    counts = df["error_type"].value_counts()

    print("\nERROR CATEGORY COUNTS")
    print("-" * 40)
    print(counts.to_string())

    plt.figure(figsize=(10, 6))

    counts.plot(
        kind="bar",
        edgecolor="black",
    )

    plt.title("Distribution of Coding Error Categories")
    plt.xlabel("Error Category")
    plt.ylabel("Number of Attempts")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()

    output_file = OUTPUT_DIR / "error_distribution.png"

    plt.savefig(output_file, dpi=150)
    plt.close()

    print(f"\nSaved: {output_file}")


# ==================================================
# 2. ERRORS BY PROGRAMMING TOPIC
# ==================================================

def plot_errors_by_topic(df):

    topic_errors = df[
        df["error_type"] != "No Error"
    ].groupby("topic").size().sort_values(ascending=False)

    print("\nINCORRECT ATTEMPTS BY TOPIC")
    print("-" * 40)
    print(topic_errors.to_string())

    plt.figure(figsize=(9, 6))

    topic_errors.plot(
        kind="bar",
        edgecolor="black",
    )

    plt.title("Incorrect Attempts by Programming Topic")
    plt.xlabel("Programming Topic")
    plt.ylabel("Number of Incorrect Attempts")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    output_file = OUTPUT_DIR / "errors_by_topic.png"

    plt.savefig(output_file, dpi=150)
    plt.close()

    print(f"\nSaved: {output_file}")


# ==================================================
# 3. CORRECT VS INCORRECT ATTEMPTS
# ==================================================

def plot_correct_vs_incorrect(df):

    correct_count = int((df["is_correct"] == 1).sum())
    incorrect_count = int((df["is_correct"] == 0).sum())

    print("\nCODING PERFORMANCE")
    print("-" * 40)
    print(f"Correct attempts: {correct_count}")
    print(f"Incorrect attempts: {incorrect_count}")

    labels = ["Correct", "Incorrect"]
    values = [correct_count, incorrect_count]

    plt.figure(figsize=(7, 6))

    plt.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
    )

    plt.title("Correct vs Incorrect Attempts")
    plt.tight_layout()

    output_file = OUTPUT_DIR / "correct_vs_incorrect.png"

    plt.savefig(output_file, dpi=150)
    plt.close()

    print(f"\nSaved: {output_file}")


# ==================================================
# 4. ACCURACY BY ATTEMPT NUMBER
# ==================================================

def plot_accuracy_by_attempt(df):

    accuracy = (
        df.groupby("attempt_number")["is_correct"]
        .mean()
        .mul(100)
    )

    print("\nCORRECT ATTEMPT RATE BY ATTEMPT NUMBER")
    print("-" * 40)
    print(accuracy.round(2).to_string())

    plt.figure(figsize=(9, 6))

    plt.plot(
        accuracy.index,
        accuracy.values,
        marker="o",
    )

    plt.title("Correct Attempt Rate by Attempt Number")
    plt.xlabel("Attempt Number")
    plt.ylabel("Correct Attempts (%)")
    plt.xticks(sorted(df["attempt_number"].unique()))
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output_file = OUTPUT_DIR / "accuracy_by_attempt.png"

    plt.savefig(output_file, dpi=150)
    plt.close()

    print(f"\nSaved: {output_file}")


# ==================================================
# 5. PREVIOUS ERRORS VS TEST PASS RATE
# ==================================================

def plot_previous_errors_vs_pass_rate(df):

    plt.figure(figsize=(9, 6))

    plt.scatter(
        df["previous_errors"],
        df["test_pass_rate"],
        alpha=0.6,
    )

    plt.title("Previous Errors vs Test Pass Rate")
    plt.xlabel("Number of Previous Errors")
    plt.ylabel("Test Pass Rate")
    plt.tight_layout()

    output_file = OUTPUT_DIR / "previous_errors_vs_pass_rate.png"

    plt.savefig(output_file, dpi=150)
    plt.close()

    print(f"\nSaved: {output_file}")


# ==================================================
# 6. SUMMARY STATISTICS
# ==================================================

def print_summary(df):

    total = len(df)

    correct = int((df["is_correct"] == 1).sum())

    incorrect = int((df["is_correct"] == 0).sum())

    accuracy = (
        correct / total * 100
        if total > 0
        else 0
    )

    print("\nFINAL SUMMARY")
    print("=" * 40)
    print(f"Total attempts: {total}")
    print(f"Correct attempts: {correct}")
    print(f"Incorrect attempts: {incorrect}")
    print(f"Overall correct attempt rate: {accuracy:.2f}%")
    print(
        "Average test pass rate: "
        f"{df['test_pass_rate'].mean():.2f}"
    )
    print(
        "Average execution time: "
        f"{df['execution_time'].mean():.3f}"
    )

    print("\nIMPORTANT DATASET LIMITATION")
    print("-" * 40)
    print(
        "This dataset is synthetically generated. "
        "The results describe simulated records, "
        "not real student performance."
    )


# ==================================================
# MAIN PROGRAM
# ==================================================

def main():

    df = load_data()

    plot_error_distribution(df)

    plot_errors_by_topic(df)

    plot_correct_vs_incorrect(df)

    plot_accuracy_by_attempt(df)

    plot_previous_errors_vs_pass_rate(df)

    print_summary(df)

    print("\n" + "=" * 60)
    print("EDA COMPLETED SUCCESSFULLY!")
    print(f"Charts saved in: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()

