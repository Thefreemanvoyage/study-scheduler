"""Pydantic request/response schemas."""
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


# ---------- Auth ----------
class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


# ---------- Subjects ----------
class SubjectBase(BaseModel):
    name: str
    total_units: int = 0
    total_hours: float = 0.0


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    total_units: Optional[int] = None
    total_hours: Optional[float] = None


class SubjectOut(SubjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Units ----------
class UnitBase(BaseModel):
    subject_id: int
    name: str
    planned_hours: float = 0.0
    completed_hours: float = 0.0


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    name: Optional[str] = None
    planned_hours: Optional[float] = None
    completed_hours: Optional[float] = None


class UnitOut(UnitBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Tasks ----------
class TaskBase(BaseModel):
    unit_id: int
    date: date
    planned_hours: float = 0.0
    completed_hours: float = 0.0
    status: str = "pending"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    date: Optional[date] = None
    planned_hours: Optional[float] = None
    completed_hours: Optional[float] = None
    status: Optional[str] = None


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Progress ----------
class SubjectProgress(BaseModel):
    subject_id: int
    subject_name: str
    planned_hours: float
    completed_hours: float
    completion_percent: float
    total_tasks: int
    completed_tasks: int
    skipped_tasks: int


class ProgressLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject_id: int
    date: date
    completion_percent: float


# ---------- Adaptive workload ----------
class WorkloadOut(BaseModel):
    subject_id: int
    subject_name: str
    remaining_hours: float          # hours still to be studied
    remaining_days: int             # days left until the last scheduled task
    original_daily_hours: float     # even spread of planned hours
    recommended_daily_hours: float  # recalculated after skips
    skipped_hours: float            # hours lost to skipped tasks
    burden_index: float             # recommended / original (1.0 = on track)


# ---------- Reminders ----------
class ReminderBase(BaseModel):
    task_id: int
    reminder_time: datetime
    status: str = "scheduled"


class ReminderCreate(ReminderBase):
    pass


class ReminderOut(ReminderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class NextReminder(BaseModel):
    reminder_id: int
    task_id: int
    reminder_time: datetime
    unit_name: str
    subject_name: str
