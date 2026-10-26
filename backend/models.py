from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
)

from database import Base


class StudentAttempt(Base):
    __tablename__ = "student_attempts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    student_id = Column(
        String(100),
        nullable=False,
        index=True,
    )

    topic = Column(
        String(100),
        nullable=False,
    )

    attempt_number = Column(
        Integer,
        nullable=False,
    )

    previous_errors = Column(
        Integer,
        nullable=False,
        default=0,
    )

    syntax_error = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    test_pass_rate = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    execution_time = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    predicted_error = Column(
        String(100),
        nullable=False,
    )

    is_correct = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
