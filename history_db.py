import sqlite3
from datetime import date, datetime
from pathlib import Path


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "lodelabels.db"


def get_connection():

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


def init_db():

    with get_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                created_at TEXT NOT NULL,
                session_date TEXT NOT NULL,

                label_type TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,

                buyer_number INTEGER NOT NULL,
                username TEXT NOT NULL,

                file_path TEXT NOT NULL,

                print_status TEXT NOT NULL
                    DEFAULT 'created',

                print_count INTEGER NOT NULL
                    DEFAULT 0,

                last_printed_at TEXT,

                last_error TEXT
            )
            """
        )

        connection.commit()


def add_label(
    label_type,
    sequence_number,
    buyer_number,
    username,
    file_path,
):

    created_at = datetime.now().isoformat(
        timespec="seconds"
    )

    session_date = date.today().isoformat()


    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO labels (
                created_at,
                session_date,
                label_type,
                sequence_number,
                buyer_number,
                username,
                file_path,
                print_status,
                print_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                session_date,
                label_type,
                sequence_number,
                buyer_number,
                username,
                str(file_path),
                "created",
                0,
            ),
        )

        connection.commit()

        return cursor.lastrowid


def mark_print_success(label_id):

    printed_at = datetime.now().isoformat(
        timespec="seconds"
    )


    with get_connection() as connection:

        connection.execute(
            """
            UPDATE labels
            SET
                print_status = 'printed',
                print_count = print_count + 1,
                last_printed_at = ?,
                last_error = NULL
            WHERE id = ?
            """,
            (
                printed_at,
                label_id,
            ),
        )

        connection.commit()


def mark_print_failure(
    label_id,
    error,
):

    with get_connection() as connection:

        connection.execute(
            """
            UPDATE labels
            SET
                print_status = 'print_failed',
                last_error = ?
            WHERE id = ?
            """,
            (
                str(error),
                label_id,
            ),
        )

        connection.commit()


def get_recent_labels(
    limit=50,
):

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM labels
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                limit,
            ),
        ).fetchall()

    return rows


def get_label(label_id):

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM labels
            WHERE id = ?
            """,
            (
                label_id,
            ),
        ).fetchone()

    return row