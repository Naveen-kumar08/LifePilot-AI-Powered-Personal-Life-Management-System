from datetime import datetime

from database import execute


# =========================================================
# GET DUE REMINDERS
# =========================================================

def get_due_reminders(user_id):

    now = datetime.now()

    today = now.strftime(
        "%Y-%m-%d"
    )

    current_time = now.strftime(
        "%H:%M"
    )

    reminders = execute(
        """
        SELECT *
        FROM reminders
        WHERE user_id=?
        AND status='Pending'
        AND
        (
            reminder_date < ?
            OR
            (
                reminder_date = ?
                AND reminder_time <= ?
            )
        )
        ORDER BY
            reminder_date,
            reminder_time
        """,
        (
            user_id,
            today,
            today,
            current_time
        ),
        fetch=True
    )

    return reminders


# =========================================================
# GET UPCOMING REMINDERS
# =========================================================

def get_upcoming_reminders(
    user_id,
    limit=10
):

    reminders = execute(
        """
        SELECT *
        FROM reminders
        WHERE user_id=?
        AND status='Pending'
        ORDER BY
            reminder_date,
            reminder_time
        LIMIT ?
        """,
        (
            user_id,
            limit
        ),
        fetch=True
    )

    return reminders


# =========================================================
# CREATE REMINDER
# =========================================================

def create_reminder(
    user_id,
    title,
    description,
    reminder_date,
    reminder_time,
    repeat_type="Once"
):

    execute(
        """
        INSERT INTO reminders
        (
            user_id,
            title,
            description,
            reminder_date,
            reminder_time,
            repeat_type,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            title,
            description,
            reminder_date,
            reminder_time,
            repeat_type,
            "Pending"
        )
    )


# =========================================================
# COMPLETE REMINDER
# =========================================================

def complete_reminder(
    reminder_id,
    user_id
):

    execute(
        """
        UPDATE reminders
        SET status='Completed'
        WHERE id=?
        AND user_id=?
        """,
        (
            reminder_id,
            user_id
        )
    )


# =========================================================
# DELETE REMINDER
# =========================================================

def delete_reminder(
    reminder_id,
    user_id
):

    execute(
        """
        DELETE FROM reminders
        WHERE id=?
        AND user_id=?
        """,
        (
            reminder_id,
            user_id
        )
    )