import streamlit as st

from database import execute


def show_notes():

    user_id = st.session_state.user_id

    st.title("📝 Notes")

    # -----------------------------------------------------
    # Add Note
    # -----------------------------------------------------

    with st.expander(
        "➕ Add Note",
        expanded=True
    ):

        with st.form("add_note"):

            title = st.text_input(
                "Title"
            )

            content = st.text_area(
                "Content",
                height=180
            )

            submitted = st.form_submit_button(
                "Save Note"
            )

            if submitted:

                if (
                    not title.strip()
                    or not content.strip()
                ):

                    st.error(
                        "Title and content are required."
                    )

                else:

                    execute(
                        """
                        INSERT INTO notes
                        (
                            user_id,
                            title,
                            content
                        )
                        VALUES (?, ?, ?)
                        """,
                        (
                            user_id,
                            title.strip(),
                            content.strip()
                        )
                    )

                    st.success(
                        "Note saved."
                    )

                    st.rerun()

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    search = st.text_input(
        "🔍 Search Notes"
    )

    if search.strip():

        rows = execute(
            """
            SELECT *
            FROM notes
            WHERE user_id=?
            AND
            (
                title LIKE ?
                OR content LIKE ?
            )
            ORDER BY updated_at DESC
            """,
            (
                user_id,
                f"%{search}%",
                f"%{search}%"
            ),
            fetch=True
        )

    else:

        rows = execute(
            """
            SELECT *
            FROM notes
            WHERE user_id=?
            ORDER BY updated_at DESC
            """,
            (user_id,),
            fetch=True
        )

    if not rows:

        st.info(
            "No notes found."
        )

        return

    # -----------------------------------------------------
    # Display Notes
    # -----------------------------------------------------

    for note in rows:

        with st.container(
            border=True
        ):

            st.subheader(
                note["title"]
            )

            st.write(
                note["content"]
            )

            if st.button(
                "🗑️ Delete",
                key=f"del_note_{note['id']}"
            ):

                execute(
                    """
                    DELETE FROM notes
                    WHERE id=?
                    AND user_id=?
                    """,
                    (
                        note["id"],
                        user_id
                    )
                )

                st.rerun()