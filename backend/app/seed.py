"""Seed the database with a demo user and the 5 example subjects.

Run from the backend directory:  python -m app.seed
Idempotent: it skips rows that already exist.
"""
from datetime import date, datetime, timedelta

from .database import Base, engine, SessionLocal
from . import models, auth, services

# Example subjects with their units and a rough hour budget each.
SEED_SUBJECTS = [
    {
        "name": "Costing Methods",
        "total_hours": 40,
        "units": [
            ("Job & Batch Costing", 8),
            ("Process Costing", 10),
            ("Standard Costing", 12),
            ("Marginal Costing", 10),
        ],
    },
    {
        "name": "GST",
        "total_hours": 35,
        "units": [
            ("Supply & Levy", 8),
            ("Input Tax Credit", 9),
            ("Returns & Payment", 8),
            ("Registration", 10),
        ],
    },
    {
        "name": "Income Tax",
        "total_hours": 45,
        "units": [
            ("Basic Concepts", 8),
            ("Heads of Income", 15),
            ("Deductions", 12),
            ("Assessment & Filing", 10),
        ],
    },
    {
        "name": "Financial Management",
        "total_hours": 38,
        "units": [
            ("Time Value of Money", 8),
            ("Capital Budgeting", 12),
            ("Cost of Capital", 10),
            ("Working Capital", 8),
        ],
    },
    {
        "name": "Advanced Accounting",
        "total_hours": 42,
        "units": [
            ("Amalgamation", 12),
            ("Consolidated Statements", 14),
            ("Partnership Accounts", 8),
            ("Banking Company Accounts", 8),
        ],
    },
]

DEMO_USER = ("student", "password123")


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # --- demo user ---
        username, password = DEMO_USER
        if not db.query(models.User).filter_by(username=username).first():
            db.add(
                models.User(
                    username=username,
                    hashed_password=auth.hash_password(password),
                )
            )
            db.commit()
            print(f"Created demo user: {username} / {password}")

        # --- subjects / units / one sample task per unit ---
        start = date.today()
        for idx, s in enumerate(SEED_SUBJECTS):
            if db.query(models.Subject).filter_by(name=s["name"]).first():
                print(f"Subject already exists, skipping: {s['name']}")
                continue

            subject = models.Subject(
                name=s["name"],
                total_units=len(s["units"]),
                total_hours=s["total_hours"],
            )
            db.add(subject)
            db.flush()  # get subject.id

            for u_idx, (uname, uhours) in enumerate(s["units"]):
                unit = models.Unit(
                    subject_id=subject.id,
                    name=uname,
                    planned_hours=uhours,
                    completed_hours=0,
                )
                db.add(unit)
                db.flush()

                # Schedule one study task for this unit, spread over the weeks.
                task_date = start + timedelta(days=(idx * 4 + u_idx))
                task = models.Task(
                    unit_id=unit.id,
                    date=task_date,
                    planned_hours=uhours,
                    completed_hours=0,
                    status="pending",
                )
                db.add(task)
                db.flush()

                # A reminder 5 minutes from now for the first task of each subject.
                if u_idx == 0:
                    db.add(
                        models.Reminder(
                            task_id=task.id,
                            reminder_time=datetime.now() + timedelta(minutes=5),
                            status="scheduled",
                        )
                    )

            db.commit()
            services.log_progress(db, subject)
            print(f"Seeded subject: {s['name']} ({len(s['units'])} units)")

        print("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
