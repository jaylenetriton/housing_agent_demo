from pathlib import Path
import sqlite3

database_path = Path(__file__).resolve().parent / "housing.db"

# All student information in this demo is fictional.
students = [
    (1001, "Alex", "Rivera", "alex.rivera@my_um.edu"),
    (1002, "Jordan", "Chen", "jordan.chen@my_um.edu"),
    (1003, "Taylor", "Brooks", "taylor.brooks@my_um.edu"),
]

connection = sqlite3.connect(database_path)

try:
    connection.executemany("""
        INSERT INTO students (
            student_id, first_name, last_name, email
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(student_id) DO NOTHING
    """, students)

    connection.commit()

    results = connection.execute("""
        SELECT student_id, first_name, last_name, email
        FROM students
        ORDER BY student_id
    """).fetchall()

    print("Students in the database:")
    for student in results:
        print(student)

finally:
    connection.close()