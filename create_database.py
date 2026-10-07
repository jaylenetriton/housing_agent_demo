from pathlib import Path
import sqlite3

# Keep the database in the same folder as this script.
database_path = Path(__file__).resolve().parent / "housing.db"

connection = sqlite3.connect(database_path)

# Enforce relationships between tables for this connection.
connection.execute("PRAGMA foreign_keys = ON")

try:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            application_id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            term TEXT NOT NULL,
            submitted_date TEXT NOT NULL,
            agreement_received INTEGER NOT NULL DEFAULT 0
                CHECK (agreement_received IN (0, 1)),
            deposit_received INTEGER NOT NULL DEFAULT 0
                CHECK (deposit_received IN (0, 1)),
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            UNIQUE (student_id, term)
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS followups (
            followup_id INTEGER PRIMARY KEY,
            application_id INTEGER NOT NULL,
            reminder_date TEXT NOT NULL,
            FOREIGN KEY (application_id)
                REFERENCES applications(application_id)
        )
    """)

    print("Followups table is ready.")
    print("Applications table is ready.")
    connection.commit()

    # Inspect the table we just created.
    columns = connection.execute("PRAGMA table_info(students)").fetchall()

    print(f"Database: {database_path}")
    print("\nStudents table columns:")
    for column in columns:
        print(f"  {column[1]}: {column[2]}")

    tables = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """).fetchall()

    for table in tables:
        print(table[0])


finally:
    connection.close()