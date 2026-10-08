from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from lifecycle import lifespan

from database import get_db
from models import Interruption, WorkSession
from schemas import (
    PauseRequest,
    SessionCreate,
    SessionResponse,
    InterruptionResponse,
    SessionHistoryItem,
    SessionHistoryResponse,
)
from sqlalchemy.orm import Session, selectinload

app = FastAPI(
    title="Deep Work Session Tracker",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post(
    "/sessions/",
    response_model=SessionResponse,
    status_code=201,
    tags=["sessions"],
    operation_id="create_session",
)
def create_session(
    data: SessionCreate,
    db: Session = Depends(get_db),
):
    work_session = WorkSession(
        title=data.title,
        goal=data.goal,
        scheduled_duration=data.duration,
        status="scheduled",
    )

    try:
        db.add(work_session)
        db.commit()
        db.refresh(work_session)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Could not save the session. Please try again.",
        ) from exc

    return work_session
@app.patch(
    "/sessions/{session_id}/start",
    response_model=SessionResponse,
    tags=["sessions"],
    operation_id="start_session",
)
def start_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    try:
        # Keep the status check and update in one SQLite transaction.
        db.execute(text("BEGIN IMMEDIATE"))

        work_session = db.get(WorkSession, session_id)

        if work_session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found.",
            )

        if work_session.status != "scheduled":
            raise HTTPException(
                status_code=409,
                detail="Only a scheduled session can be started.",
            )

        work_session.status = "active"

        # Store UTC consistently with SQLite's CURRENT_TIMESTAMP.
        work_session.start_time = datetime.now(
            timezone.utc
        ).replace(tzinfo=None)

        db.commit()
        db.refresh(work_session)

        return work_session

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Could not start the session. Please try again.",
        ) from exc
        
@app.patch(
    "/sessions/{session_id}/pause",
    response_model=SessionResponse,
    tags=["sessions"],
    operation_id="pause_session",
    responses={
        404: {"description": "Session not found"},
        409: {"description": "Session is not active"},
        503: {"description": "Database operation failed"},
    },
)
def pause_session(
    session_id: int,
    data: PauseRequest,
    db: Session = Depends(get_db),
):
    try:
        db.execute(text("BEGIN IMMEDIATE"))

        work_session = db.get(WorkSession, session_id)

        if work_session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found.",
            )

        if work_session.status != "active":
            raise HTTPException(
                status_code=409,
                detail="Only an active session can be paused.",
            )

        previous_pauses = db.scalar(
            select(func.count())
            .select_from(Interruption)
            .where(Interruption.session_id == session_id)
        )

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        interruption = Interruption(
            session_id=session_id,
            reason=data.reason,
            pause_time=now,
        )
        db.add(interruption)

        if previous_pauses + 1 > 3:
            work_session.status = "interrupted"
            work_session.end_time = now
        else:
            work_session.status = "paused"

        db.commit()
        db.refresh(work_session)

        return work_session

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Could not pause the session. Please try again.",
        ) from exc


@app.patch(
    "/sessions/{session_id}/resume",
    response_model=SessionResponse,
    tags=["sessions"],
    operation_id="resume_session",
    responses={
        404: {"description": "Session not found"},
        409: {"description": "Session cannot be resumed"},
        503: {"description": "Database operation failed"},
    },
)
def resume_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    try:
        db.execute(text("BEGIN IMMEDIATE"))

        work_session = db.get(WorkSession, session_id)

        if work_session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found.",
            )

        if work_session.status != "paused":
            raise HTTPException(
                status_code=409,
                detail="Only a paused session can be resumed.",
            )

        if work_session.start_time is None:
            raise HTTPException(
                status_code=409,
                detail="Session has no start time.",
            )

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        elapsed_seconds = (
            now - work_session.start_time
        ).total_seconds()

        allowed_seconds = work_session.scheduled_duration * 66

        if elapsed_seconds > allowed_seconds:
            work_session.status = "abandoned"
            work_session.end_time = now

            # Save abandonment before returning the conflict.
            db.commit()

            raise HTTPException(
                status_code=409,
                detail="Session was abandoned because its deadline passed.",
            )

        work_session.status = "active"

        db.commit()
        db.refresh(work_session)

        return work_session

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Could not resume the session. Please try again.",
        ) from exc
@app.patch(
    "/sessions/{session_id}/complete",
    response_model=SessionResponse,
    tags=["sessions"],
    operation_id="complete_session",
    responses={
        404: {"description": "Session not found"},
        409: {"description": "Session is not active"},
        503: {"description": "Database operation failed"},
    },
)
def complete_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    try:
        db.execute(text("BEGIN IMMEDIATE"))

        work_session = db.get(WorkSession, session_id)

        if work_session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found.",
            )

        if work_session.status != "active":
            raise HTTPException(
                status_code=409,
                detail="Only an active session can be completed.",
            )

        if work_session.start_time is None:
            raise HTTPException(
                status_code=409,
                detail="Session has no start time.",
            )

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        elapsed_seconds = (
            now - work_session.start_time
        ).total_seconds()

        # Planned minutes plus a 10% allowance.
        allowed_seconds = work_session.scheduled_duration * 66

        if elapsed_seconds <= allowed_seconds:
            work_session.status = "completed"
        else:
            work_session.status = "overdue"

        work_session.end_time = now

        db.commit()
        db.refresh(work_session)

        return work_session

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Could not complete the session. Please try again.",
        ) from exc        
        
        
@app.get(
    "/sessions/history",
    response_model=SessionHistoryResponse,
    tags=["sessions"],
    operation_id="get_session_history",
)
def get_session_history(db: Session = Depends(get_db)):
    try:
        work_sessions = db.scalars(
            select(WorkSession)
            .options(selectinload(WorkSession.interruptions))
            .order_by(WorkSession.created_at.desc(), WorkSession.id.desc())
        ).all()

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        history = []
        completed_count = 0
        finished_count = 0

        terminal_statuses = {
            "completed",
            "overdue",
            "interrupted",
            "abandoned",
        }

        for work_session in work_sessions:
            elapsed_minutes = 0.0

            if work_session.start_time is not None:
                finish_time = work_session.end_time or now
                elapsed_minutes = max(
                    0.0,
                    (finish_time - work_session.start_time).total_seconds()
                    / 60,
                )

            interruptions = [
                InterruptionResponse.model_validate(item)
                for item in work_session.interruptions
            ]

            session_data = SessionResponse.model_validate(
                work_session
            ).model_dump()

            history.append(
                SessionHistoryItem(
                    **session_data,
                    elapsed_minutes=round(elapsed_minutes, 2),
                    pause_count=len(interruptions),
                    interruptions=interruptions,
                )
            )

            if work_session.status == "completed":
                completed_count += 1

            if work_session.status in terminal_statuses:
                finished_count += 1

        completion_ratio = (
            completed_count / finished_count
            if finished_count > 0
            else 0.0
        )

        return SessionHistoryResponse(
            sessions=history,
            total_sessions=len(history),
            finished_sessions=finished_count,
            completed_sessions=completed_count,
            completion_ratio=round(completion_ratio, 4),
        )

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Could not load session history. Please try again.",
        ) from exc        