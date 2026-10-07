from pathlib import Path
import sqlite3

database_path = Path(__file__).resolve().parent / "housing.db"

# application_id, student_id, term, submitted_date,
# agreement_received, deposit_received
applications = [
    (2001, 1001, "Fall 2027", "2026-10-01", 1, 0),
    (2002, 1002, "Fall 2027", "2026-10-02", 0, 0),
    (2003, 1003, "Fall 2027", "2026-10-03", 1, 1),
]

connection = sqlite3.connect(database_path)
connection.execute("PRAGMA foreign_keys = ON")

try:
    connection.executemany("""
        INSERT INTO applications (
            application_id,
            student_id,
            term,
            submitted_date,
            agreement_received,
            deposit_received
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(application_id) DO NOTHING
    """, applications)

    connection.commit()

    # Join applications to students so we can display their names.
    results = connection.execute("""
        SELECT
            a.application_id,
            s.first_name,
            s.last_name,
            a.agreement_received,
            a.deposit_received
        FROM applications AS a
        JOIN students AS s ON a.student_id = s.student_id
        WHERE a.agreement_received = 0
           OR a.deposit_received = 0
        ORDER BY a.application_id
    """).fetchall()

    print("Incomplete applications:")

    for application_id, first_name, last_name, agreement, deposit in results:
        missing = []

        if agreement == 0:
            missing.append("agreement")

        if deposit == 0:
            missing.append("deposit")

        print(
            f"{application_id}: {first_name} {last_name}"
            f" — Missing: {', '.join(missing)}"
        )

finally:
    connection.close()