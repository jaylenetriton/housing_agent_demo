from datetime import date, timedelta
from pathlib import Path
import sqlite3

DATABASE_PATH = Path(__file__).resolve().parent / "housing.db"


def get_applications_needing_followup(as_of_date: str) -> list[dict]:
    """Return incomplete applications due for follow-up on YYYY-MM-DD."""

    report_date = date.fromisoformat(as_of_date)
    waiting_days = 3
    cutoff_date = (
        report_date - timedelta(days=waiting_days)
    ).isoformat()

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute("""
            SELECT
                a.application_id,
                s.first_name,
                s.last_name,
                s.email,
                a.submitted_date,
                a.agreement_received,
                a.deposit_received,
                MAX(f.reminder_date) AS last_reminder,
                COUNT(f.followup_id) AS reminder_count
            FROM applications AS a
            JOIN students AS s
                ON a.student_id = s.student_id
            LEFT JOIN followups AS f
                ON a.application_id = f.application_id
            WHERE a.agreement_received = 0
               OR a.deposit_received = 0
            GROUP BY
                a.application_id,
                s.first_name,
                s.last_name,
                s.email,
                a.submitted_date,
                a.agreement_received,
                a.deposit_received
            HAVING COALESCE(
                MAX(f.reminder_date), a.submitted_date
            ) <= ?
            ORDER BY a.application_id
        """, (cutoff_date,)).fetchall()

        applications = []

        for row in rows:
            application = dict(row)
            missing = []

            if application["agreement_received"] == 0:
                missing.append("agreement")

            if application["deposit_received"] == 0:
                missing.append("deposit")

            application["missing_requirements"] = missing
            applications.append(application)

        return applications

    finally:
        connection.close()

def get_application_details(application_id: int) -> dict:
    """Return an application's current details and reminder history."""

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        row = connection.execute("""
            SELECT
                a.application_id,
                a.term,
                a.submitted_date,
                a.agreement_received,
                a.deposit_received,
                s.student_id,
                s.first_name,
                s.last_name,
                s.email
            FROM applications AS a
            JOIN students AS s
                ON a.student_id = s.student_id
            WHERE a.application_id = ?
        """, (application_id,)).fetchone()

        if row is None:
            return {
                "found": False,
                "application_id": application_id,
                "message": "No application found with this ID."
            }

        application = dict(row)
        application["found"] = True

        missing = []

        if application["agreement_received"] == 0:
            missing.append("agreement")

        if application["deposit_received"] == 0:
            missing.append("deposit")

        application["missing_requirements"] = missing

        reminders = connection.execute("""
            SELECT followup_id, reminder_date
            FROM followups
            WHERE application_id = ?
            ORDER BY reminder_date, followup_id
        """, (application_id,)).fetchall()

        application["reminders"] = [
            dict(reminder) for reminder in reminders
        ]
        application["reminder_count"] = len(reminders)

        # Calculate the next eligible date using our three-day rule.
        reference_date = (
            reminders[-1]["reminder_date"]
            if reminders
            else application["submitted_date"]
        )

        application["next_followup_due"] = (
            (
                date.fromisoformat(reference_date)
                + timedelta(days=3)
            ).isoformat()
            if missing
            else None
        )

        return application

    finally:
        connection.close()