from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from ml.predict import predict_error
from models import StudentAttempt
from schemas import (
    AttemptCreate,
    AttemptResponse,
    PredictionRequest,
)


# ==================================================
# APPLICATION STARTUP
# ==================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="CodeHabit API",
    description=(
        "An educational coding-practice API with ML-based "
        "error-category predictions."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ==================================================
# CORS CONFIGURATION
# ==================================================

# Development configuration for the local Vite frontend.
# Restrict origins before deploying publicly.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# HELPER FUNCTION
# ==================================================

def get_prediction(payload):
    try:
        result = predict_error(
            topic=payload.topic,
            attempt_number=payload.attempt_number,
            previous_errors=payload.previous_errors,
            syntax_error=payload.syntax_error,
            test_pass_rate=payload.test_pass_rate,
            execution_time=payload.execution_time,
        )

        return result

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Log the underlying exception on the server.
        print(f"Prediction error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="The prediction could not be completed.",
        ) from exc


# ==================================================
# HOME ENDPOINT
# ==================================================

@app.get("/")
def home():
    return {
        "message": "CodeHabit Backend is running!",
        "version": "1.0.0",
        "docs": "/docs",
    }


# ==================================================
# HEALTH ENDPOINT
# ==================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": "CodeHabit",
    }


# ==================================================
# PREDICTION ENDPOINT
# ==================================================

@app.post("/api/predict")
def predict(payload: PredictionRequest):
    result = get_prediction(payload)

    return {
        "success": True,
        "prediction": result,
    }


# ==================================================
# SAVE STUDENT ATTEMPT
# ==================================================

@app.post(
    "/api/attempts",
    response_model=AttemptResponse,
)
def create_attempt(
    payload: AttemptCreate,
    db: Session = Depends(get_db),
):
    prediction = get_prediction(payload)

    record = StudentAttempt(
        student_id=payload.student_id,
        topic=payload.topic.strip(),
        attempt_number=payload.attempt_number,
        previous_errors=payload.previous_errors,
        syntax_error=bool(payload.syntax_error),
        test_pass_rate=payload.test_pass_rate,
        execution_time=payload.execution_time,
        predicted_error=prediction["predicted_error"],
        is_correct=payload.is_correct,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


# ==================================================
# VIEW SAVED ATTEMPTS
# ==================================================

@app.get(
    "/api/attempts",
    response_model=list[AttemptResponse],
)
def get_attempts(
    student_id: str = Query(
        min_length=1,
        max_length=100,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    db: Session = Depends(get_db),
):
    records = (
        db.query(StudentAttempt)
        .filter(StudentAttempt.student_id == student_id)
        .order_by(StudentAttempt.id.desc())
        .limit(limit)
        .all()
    )

    return records


# ==================================================
# DASHBOARD SUMMARY
# ==================================================

@app.get("/api/dashboard/{student_id}")
def get_dashboard(
    student_id: str,
    db: Session = Depends(get_db),
):
    records = (
        db.query(StudentAttempt)
        .filter(StudentAttempt.student_id == student_id)
        .all()
    )

    total_attempts = len(records)

    correct_attempts = sum(
        1 for record in records if record.is_correct
    )

    incorrect_attempts = total_attempts - correct_attempts

    accuracy = (
        round(correct_attempts / total_attempts * 100, 2)
        if total_attempts
        else 0.0
    )

    error_counts = {}

    for record in records:
        category = record.predicted_error

        if category != "No Error":
            error_counts[category] = (
                error_counts.get(category, 0) + 1
            )

    return {
        "student_id": student_id,
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "incorrect_attempts": incorrect_attempts,
        "accuracy_percentage": accuracy,
        "predicted_error_counts": error_counts,
    }

