from pathlib import Path
import sqlite3

database_path = Path(__file__).resolve().parent / "housing.db"

connection = sqlite3.connect(database_path)
connection.execute("PRAGMA foreign_keys = ON")

try:
    # Simulated history only: this does not send a message.
    connection.execute("""
        INSERT INTO followups (
            followup_id, application_id, reminder_date
        )
        VALUES (?, ?, ?)
        ON CONFLICT(followup_id) DO NOTHING
    """, (3001, 2001, "2026-10-04"))

    connection.commit()

    results = connection.execute("""
        SELECT
            a.application_id,
            s.first_name,
            s.last_name,
            COUNT(f.followup_id) AS reminder_count,
            MAX(f.reminder_date) AS last_reminder
        FROM applications AS a
        JOIN students AS s ON a.student_id = s.student_id
        LEFT JOIN followups AS f
            ON a.application_id = f.application_id
        GROUP BY a.application_id, s.first_name, s.last_name
        ORDER BY a.application_id
    """).fetchall()

    for application_id, first_name, last_name, count, last_date in results:
        print(
            f"{application_id}: {first_name} {last_name}"
            f" | Reminders: {count}"
            f" | Last reminder: {last_date or 'Never'}"
        )

finally:
    connection.close()