import sqlite3
from pathlib import Path

from database import engine


def load_seed():
    sql_path = Path(__file__).resolve().parent / "seed_data.sql"
    sql = sql_path.read_text(encoding="utf-8-sig")

    connection = engine.raw_connection()

    try:
        cursor = connection.cursor()

        try:
            cursor.executescript(sql)
            cursor.execute(
                "SELECT COUNT(*) FROM sessions WHERE title IN (?, ?, ?)",
                (
                    "Demo: Learn FastAPI",
                    "Demo: Practice Python testing",
                    "Demo: Review React",
                ),
            )
            count = cursor.fetchone()[0]
        finally:
            cursor.close()

        print(f"Seed loaded successfully. Demo sessions: {count}")

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    load_seed()