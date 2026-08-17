from datetime import date

import streamlit as st

from database import execute


def show_tasks():

    user_id = st.session_state.user_id

    st.title("✅ Tasks")

    # -----------------------------------------------------
    # Add Task
    # -----------------------------------------------------

    with st.expander(
        "➕ Add Task",
        expanded=True
    ):

        with st.form("add_task"):

            title = st.text_input(
                "Task Title"
            )

            description = st.text_area(
                "Description"
            )

            priority = st.selectbox(
                "Priority",
                [
                    "Low",
                    "Medium",
                    "High",
                    "Urgent"
                ]
            )

            due_date = st.date_input(
                "Due Date",
                value=date.today()
            )

            submitted = st.form_submit_button(
                "Add Task"
            )

            if submitted:

                if not title.strip():

                    st.error(
                        "Enter a task title."
                    )

                else:

                    execute(
                        """
                        INSERT INTO tasks
                        (
                            user_id,
                            title,
                            description,
                            priority,
                            due_date
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            user_id,
                            title.strip(),
                            description,
                            priority,
                            due_date.isoformat()
                        )
                    )

                    st.success(
                        "Task added."
                    )

                    st.rerun()

    st.subheader(
        "Your Tasks"
    )

    # -----------------------------------------------------
    # Get Tasks
    # -----------------------------------------------------

    rows = execute(
        """
        SELECT *
        FROM tasks
        WHERE user_id=?
        ORDER BY
            status='Completed',
            due_date
        """,
        (user_id,),
        fetch=True
    )

    if not rows:

        st.info(
            "No tasks yet."
        )

        return

    # -----------------------------------------------------
    # Display Tasks
    # -----------------------------------------------------

    for task in rows:

        with st.container(
            border=True
        ):

            c1, c2, c3 = st.columns(
                [5, 2, 1]
            )

            with c1:

                st.markdown(
                    f"**{task['title']}**"
                )

                if task["description"]:

                    st.caption(
                        task["description"]
                    )

            with c2:

                st.write(
                    f"{task['priority']} | "
                    f"{task['due_date'] or 'No date'}"
                )

            with c3:

                if task["status"] == "Completed":

                    st.success(
                        "Done"
                    )

                else:

                    if st.button(
                        "✓",
                        key=f"complete_{task['id']}"
                    ):

                        execute(
                            """
                            UPDATE tasks
                            SET status='Completed'
                            WHERE id=?
                            AND user_id=?
                            """,
                            (
                                task["id"],
                                user_id
                            )
                        )

                        st.rerun()

            if st.button(
                "🗑️ Delete",
                key=f"delete_task_{task['id']}"
            ):

                execute(
                    """
                    DELETE FROM tasks
                    WHERE id=?
                    AND user_id=?
                    """,
                    (
                        task["id"],
                        user_id
                    )
                )

                st.rerun()