"""SQLAlchemy ORM models mapping to the PostgreSQL schema."""
from datetime import date, datetime

from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """Account for the simple username/password login."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    total_units = Column(Integer, default=0)
    total_hours = Column(Float, default=0.0)

    # Deleting a subject cascades to its units, tasks and logs.
    units = relationship(
        "Unit", back_populates="subject", cascade="all, delete-orphan"
    )
    progress_logs = relationship(
        "ProgressLog", back_populates="subject", cascade="all, delete-orphan"
    )


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    planned_hours = Column(Float, default=0.0)
    completed_hours = Column(Float, default=0.0)

    subject = relationship("Subject", back_populates="units")
    tasks = relationship(
        "Task", back_populates="unit", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(
        Integer, ForeignKey("units.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False, default=date.today)
    planned_hours = Column(Float, default=0.0)
    completed_hours = Column(Float, default=0.0)
    # One of: "pending", "completed", "skipped".
    status = Column(String, default="pending", nullable=False)

    unit = relationship("Unit", back_populates="tasks")
    reminders = relationship(
        "Reminder", back_populates="task", cascade="all, delete-orphan"
    )


class ProgressLog(Base):
    __tablename__ = "progress_logs"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False, default=date.today)
    completion_percent = Column(Float, default=0.0)

    subject = relationship("Subject", back_populates="progress_logs")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    reminder_time = Column(DateTime, nullable=False)
    # One of: "scheduled", "sent", "dismissed".
    status = Column(String, default="scheduled", nullable=False)

    task = relationship("Task", back_populates="reminders")
