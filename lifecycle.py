import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from database import SessionLocal
from models import WorkSession


logger = logging.getLogger(__name__)


def abandon_expired_sessions():
    with SessionLocal() as db:
        try:
            db.execute(text("BEGIN IMMEDIATE"))

            paused_sessions = db.scalars(
                select(WorkSession).where(
                    WorkSession.status == "paused",
                    WorkSession.start_time.is_not(None),
                )
            ).all()

            now = datetime.now(timezone.utc).replace(tzinfo=None)

            for work_session in paused_sessions:
                elapsed_seconds = (
                    now - work_session.start_time
                ).total_seconds()

                allowed_seconds = (
                    work_session.scheduled_duration * 66
                )

                if elapsed_seconds > allowed_seconds:
                    work_session.status = "abandoned"
                    work_session.end_time = now

            db.commit()

        except SQLAlchemyError:
            db.rollback()
            raise


async def monitor_paused_sessions(stop_event):
    while not stop_event.is_set():
        try:
            await asyncio.to_thread(abandon_expired_sessions)
        except SQLAlchemyError:
            logger.exception("Automatic abandonment check failed")

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=5)
        except asyncio.TimeoutError:
            pass


@asynccontextmanager
async def lifespan(app):
    stop_event = asyncio.Event()
    monitor_task = asyncio.create_task(
        monitor_paused_sessions(stop_event)
    )

    try:
        yield
    finally:
        stop_event.set()
        await monitor_task