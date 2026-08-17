from datetime import date

import streamlit as st

from database import execute


def show_dashboard():

    user_id = st.session_state.user_id

    today = date.today().isoformat()

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    pending = execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE user_id=?
        AND status != 'Completed'
        """,
        (user_id,),
        fetch=True
    )[0][0]

    completed = execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE user_id=?
        AND status='Completed'
        """,
        (user_id,),
        fetch=True
    )[0][0]

    overdue = execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE user_id=?
        AND status!='Completed'
        AND due_date < ?
        AND due_date IS NOT NULL
        """,
        (
            user_id,
            today
        ),
        fetch=True
    )[0][0]

    month = today[:7]

    expense_total = execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE user_id=?
        AND substr(expense_date,1,7)=?
        """,
        (
            user_id,
            month
        ),
        fetch=True
    )[0][0]

    # -----------------------------------------------------
    # Upcoming Tasks
    # -----------------------------------------------------

    upcoming_tasks = execute(
        """
        SELECT *
        FROM tasks
        WHERE user_id=?
        AND status!='Completed'
        ORDER BY
            due_date IS NULL,
            due_date
        LIMIT 8
        """,
        (user_id,),
        fetch=True
    )

    # -----------------------------------------------------
    # Expiring Documents
    # -----------------------------------------------------

    expiring_docs = execute(
        """
        SELECT *
        FROM documents
        WHERE user_id=?
        AND expiry_date IS NOT NULL
        AND expiry_date <= date(?, '+30 day')
        ORDER BY expiry_date
        """,
        (
            user_id,
            today
        ),
        fetch=True
    )

    # -----------------------------------------------------
    # Expiring Warranties
    # -----------------------------------------------------

    expiring_warranties = execute(
        """
        SELECT *
        FROM warranties
        WHERE user_id=?
        AND warranty_expiry <= date(?, '+30 day')
        ORDER BY warranty_expiry
        """,
        (
            user_id,
            today
        ),
        fetch=True
    )

    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------

    st.title("🏠 Dashboard")

    st.caption(
        "A quick view of what needs your attention."
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Pending Tasks",
        pending
    )

    c2.metric(
        "Completed Tasks",
        completed
    )

    c3.metric(
        "Overdue Tasks",
        overdue
    )

    c4.metric(
        "This Month",
        f"₹{expense_total:,.2f}"
    )

    st.divider()

    left, right = st.columns(2)

    # -----------------------------------------------------
    # Tasks
    # -----------------------------------------------------

    with left:

        st.subheader(
            "📅 Upcoming Tasks"
        )

        if not upcoming_tasks:

            st.info(
                "No pending tasks."
            )

        for task in upcoming_tasks:

            due = (
                task["due_date"]
                or "No due date"
            )

            st.write(
                f"**{task['title']}** — "
                f"{due} — {task['priority']}"
            )

    # -----------------------------------------------------
    # Expiry
    # -----------------------------------------------------

    with right:

        st.subheader(
            "⚠️ Expiring Soon"
        )

        if (
            not expiring_docs
            and not expiring_warranties
        ):

            st.success(
                "Nothing is expiring in the next 30 days."
            )

        for document in expiring_docs:

            st.warning(
                f"📄 {document['name']} — "
                f"expires {document['expiry_date']}"
            )

        for warranty in expiring_warranties:

            st.warning(
                f"🛡️ {warranty['product_name']} — "
                f"warranty ends "
                f"{warranty['warranty_expiry']}"
            )

    st.divider()

    st.subheader("💡 LifePilot")

    st.write(
        "Use the sidebar to manage your personal "
        "tasks, reminders, documents, expenses, "
        "warranties, notes and memories."
    )