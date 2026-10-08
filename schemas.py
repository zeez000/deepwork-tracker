from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    title: str = Field(min_length=1, max_length=200)
    goal: str | None = Field(default=None, max_length=2000)
    duration: int = Field(
        gt=0,
        le=1440,
        strict=True,
        description="Planned duration in whole minutes",
    )


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    goal: str | None
    scheduled_duration: int
    status: str
    start_time: datetime | None
    end_time: datetime | None
    created_at: datetime


class PauseRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    reason: str = Field(min_length=1, max_length=500)
    
    
    
    
    
class InterruptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reason: str
    pause_time: datetime


class SessionHistoryItem(SessionResponse):
    elapsed_minutes: float
    pause_count: int
    interruptions: list[InterruptionResponse]


class SessionHistoryResponse(BaseModel):
    sessions: list[SessionHistoryItem]
    total_sessions: int
    finished_sessions: int
    completed_sessions: int
    completion_ratio: float   