import sqlite3
import os


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "database"
)

DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "life_admin.db"
)


# ============================================================
# CREATE DATABASE DIRECTORY
# ============================================================

os.makedirs(
    DATABASE_DIR,
    exist_ok=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# EXECUTE SQL
# ============================================================

def execute(
    query,
    params=(),
    fetch=False,
    fetchone=False,
    commit=True
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            query,
            params
        )

        result = None

        if fetchone:

            result = cursor.fetchone()

        elif fetch:

            result = cursor.fetchall()

        if commit:

            connection.commit()

        return result

    finally:

        connection.close()


# ============================================================
# CHECK TABLE COLUMN
# ============================================================

def column_exists(
    table_name,
    column_name
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            f"PRAGMA table_info({table_name})"
        )

        columns = cursor.fetchall()

        for column in columns:

            if column["name"] == column_name:

                return True

        return False

    finally:

        connection.close()


# ============================================================
# ADD COLUMN SAFELY
# ============================================================

def add_column_if_missing(
    table_name,
    column_name,
    column_definition
):

    if not column_exists(
        table_name,
        column_name
    ):

        execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name}
            {column_definition}
            """
        )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():

    connection = get_connection()

    cursor = connection.cursor()

    # ========================================================
    # USERS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
    )


    # ========================================================
    # REMINDERS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            title TEXT NOT NULL,

            description TEXT,

            reminder_date TEXT NOT NULL,

            reminder_time TEXT NOT NULL,

            alarm_enabled INTEGER DEFAULT 1,

            status TEXT DEFAULT 'Pending',

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
        """
    )


    # ========================================================
    # TASKS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            title TEXT NOT NULL,

            description TEXT,

            due_date TEXT,

            status TEXT DEFAULT 'Pending',

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
        """
    )


    # ========================================================
    # DOCUMENTS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            title TEXT,

            file_name TEXT,

            file_path TEXT,

            document_type TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
        """
    )


    # ========================================================
    # EXPENSES
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            title TEXT NOT NULL,

            amount REAL DEFAULT 0,

            category TEXT,

            expense_date TEXT,

            description TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
        """
    )


    # ========================================================
    # WARRANTIES
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS warranties (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            product_name TEXT NOT NULL,

            purchase_date TEXT,

            expiry_date TEXT,

            description TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
        """
    )


    # ========================================================
    # NOTES
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            title TEXT NOT NULL,

            content TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
        """
    )


    # ========================================================
    # MEMORIES
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            title TEXT NOT NULL,

            content TEXT,

            memory_date TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
        """
    )


    # ========================================================
    # COMMIT
    # ========================================================

    connection.commit()

    connection.close()


    # ========================================================
    # DATABASE MIGRATION
    # ========================================================

    migrate_database()


# ============================================================
# DATABASE MIGRATION
# ============================================================

def migrate_database():

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    if not column_exists(
        "users",
        "password_hash"
    ):

        add_column_if_missing(
            "users",
            "password_hash",
            "TEXT"
        )


    # --------------------------------------------------------
    # REMINDERS
    # --------------------------------------------------------

    add_column_if_missing(
        "reminders",
        "description",
        "TEXT"
    )

    add_column_if_missing(
        "reminders",
        "reminder_date",
        "TEXT"
    )

    add_column_if_missing(
        "reminders",
        "reminder_time",
        "TEXT"
    )

    add_column_if_missing(
        "reminders",
        "alarm_enabled",
        "INTEGER DEFAULT 1"
    )

    add_column_if_missing(
        "reminders",
        "status",
        "TEXT DEFAULT 'Pending'"
    )

    add_column_if_missing(
        "reminders",
        "created_at",
        "TIMESTAMP"
    )


# ============================================================
# START DATABASE
# ============================================================

init_db()