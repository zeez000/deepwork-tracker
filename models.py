from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class WorkSession(Base):
    __tablename__ = "sessions"

    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'active', 'paused', "
            "'completed', 'interrupted', 'abandoned', 'overdue')",
            name="ck_sessions_status",
        ),
        CheckConstraint(
            "scheduled_duration > 0",
            name="ck_sessions_positive_duration",
        ),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Planned duration in minutes.
    scheduled_duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Times stay empty until the session starts or ends.
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="scheduled",
        server_default="scheduled",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    interruptions: Mapped[list["Interruption"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Interruption.id",
    )


class Interruption(Base):
    __tablename__ = "interruptions"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reason: Mapped[str] = mapped_column(Text, nullable=False)

    pause_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    session: Mapped["WorkSession"] = relationship(
        back_populates="interruptions",
    )