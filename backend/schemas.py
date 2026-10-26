from pydantic import BaseModel, ConfigDict, Field


# Data required when requesting an ML prediction
class PredictionRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=100)
    attempt_number: int = Field(ge=1, le=1000)
    previous_errors: int = Field(ge=0, le=1000)
    syntax_error: int = Field(ge=0, le=1)
    test_pass_rate: float = Field(ge=0.0, le=1.0)
    execution_time: float = Field(ge=0.0, le=3600.0)


# Data required when saving a student attempt
class AttemptCreate(PredictionRequest):
    student_id: str = Field(min_length=1, max_length=100)
    is_correct: bool = False


# Data returned when displaying an attempt
class AttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: str
    topic: str
    attempt_number: int
    previous_errors: int
    syntax_error: bool
    test_pass_rate: float
    execution_time: float
    predicted_error: str
    is_correct: bool

