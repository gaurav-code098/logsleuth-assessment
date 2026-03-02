from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

# 1. What the React app sends us
class LogSubmissionRequest(BaseModel):
    raw_log: str = Field(..., min_length=10, description="The raw server log text")

    @field_validator('raw_log')
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Log content cannot be purely whitespace.")
        return v

# 2. What we force the Groq AI to return
class GroqAnalysisResult(BaseModel):
    severity: str = Field(description="Must be Critical, Warning, or Info")
    root_cause: str = Field(description="A concise summary of the error's root cause")
    suggested_fix: str = Field(description="Actionable steps to resolve the issue")

# 3. What we send back to the React app
class LogAnalysisResponse(BaseModel):
    id: int
    raw_log: str
    status: str
    severity: Optional[str] = None
    root_cause: Optional[str] = None
    suggested_fix: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # Tells Pydantic to read data from our SQLAlchemy model