import csv
import random
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

SEED = 42
TOTAL_STUDENTS = 100
ATTEMPTS_PER_STUDENT = 10
TOTAL_RECORDS = TOTAL_STUDENTS * ATTEMPTS_PER_STUDENT

random.seed(SEED)

# Find the backend folder automatically
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Create the data folder if it does not exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_DIR / "student_attempts.csv"

# --------------------------------------------------
# DATASET CATEGORIES
# --------------------------------------------------

TOPICS = [
    "Variables",
    "Conditional Statements",
    "Loops",
    "Functions",
    "Lists",
    "Strings",
]

ERROR_TYPES = [
    "Syntax Error",
    "Incorrect Condition",
    "Loop Logic Error",
    "Variable Misuse",
    "Incorrect Output",
    "No Error",
]

# Simulated error probabilities for each topic.
# These probabilities are for creating sample data,
# not measurements of real student behaviour.

TOPIC_ERROR_WEIGHTS = {
    "Variables": [
        0.20, 0.05, 0.05, 0.30, 0.25, 0.15
    ],
    "Conditional Statements": [
        0.15, 0.35, 0.05, 0.10, 0.20, 0.15
    ],
    "Loops": [
        0.10, 0.15, 0.35, 0.10, 0.15, 0.15
    ],
    "Functions": [
        0.20, 0.10, 0.10, 0.20, 0.25, 0.15
    ],
    "Lists": [
        0.15, 0.10, 0.15, 0.20, 0.25, 0.15
    ],
    "Strings": [
        0.15, 0.10, 0.05, 0.20, 0.35, 0.15
    ],
}


# --------------------------------------------------
# GENERATE ONE ATTEMPT
# --------------------------------------------------

def generate_record(student_number, attempt_number):
    topic = random.choice(TOPICS)

    # Simulate a student who gradually improves.
    previous_errors = max(
        0,
        min(
            10,
            int(
                random.gauss(
                    5 - attempt_number * 0.25,
                    2
                )
            )
        ),
    )

    # Select a simulated error category.
    error_type = random.choices(
        ERROR_TYPES,
        weights=TOPIC_ERROR_WEIGHTS[topic],
        k=1,
    )[0]

    # Later attempts have a somewhat higher chance
    # of being correct. This is a simulation only.
    correct_probability = min(
        0.75,
        0.15 + (attempt_number * 0.05),
    )

    if random.random() < correct_probability:
        error_type = "No Error"

    is_correct = 1 if error_type == "No Error" else 0

    if is_correct:
        test_pass_rate = round(
            random.uniform(0.80, 1.00),
            2,
        )
        execution_time = round(
            random.uniform(0.01, 0.30),
            3,
        )
        syntax_error = 0
    else:
        test_pass_rate = round(
            random.uniform(0.00, 0.70),
            2,
        )

        execution_time = round(
            random.uniform(0.01, 1.50),
            3,
        )

        syntax_error = (
            1 if error_type == "Syntax Error" else 0
        )

    return {
        "student_id": f"STU{student_number:03d}",
        "exercise_id": f"EX{random.randint(1, 30):03d}",
        "topic": topic,
        "attempt_number": attempt_number,
        "previous_errors": previous_errors,
        "syntax_error": syntax_error,
        "test_pass_rate": test_pass_rate,
        "execution_time": execution_time,
        "error_type": error_type,
        "is_correct": is_correct,
    }


# --------------------------------------------------
# GENERATE THE COMPLETE DATASET
# --------------------------------------------------

def generate_dataset():
    columns = [
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

    records = []

    for student_number in range(1, TOTAL_STUDENTS + 1):
        for attempt_number in range(
            1,
            ATTEMPTS_PER_STUDENT + 1,
        ):
            record = generate_record(
                student_number,
                attempt_number,
            )
            records.append(record)

    # Shuffle rows so they are not grouped by student.
    random.shuffle(records)

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
        )
        writer.writeheader()
        writer.writerows(records)

    print("=" * 50)
    print("CodeHabit dataset generated successfully!")
    print("=" * 50)
    print(f"Total records: {len(records)}")
    print(f"Total students: {TOTAL_STUDENTS}")
    print(f"Attempts per student: {ATTEMPTS_PER_STUDENT}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    generate_dataset()
