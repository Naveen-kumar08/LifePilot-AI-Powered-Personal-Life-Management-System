import streamlit as st

from database import execute


def show_memories():

    user_id = st.session_state.user_id

    st.title("🧠 Memories")

    st.caption(
        "Store useful information you do not want to forget."
    )

    # -----------------------------------------------------
    # Add Memory
    # -----------------------------------------------------

    with st.expander(
        "➕ Remember Something",
        expanded=True
    ):

        with st.form("add_memory"):

            title = st.text_input(
                "What is it?"
            )

            content = st.text_area(
                "Information"
            )

            location = st.text_input(
                "Location (optional)"
            )

            submitted = st.form_submit_button(
                "Save Memory"
            )

            if submitted:

                if (
                    not title.strip()
                    or not content.strip()
                ):

                    st.error(
                        "Title and information are required."
                    )

                else:

                    execute(
                        """
                        INSERT INTO memories
                        (
                            user_id,
                            title,
                            content,
                            location
                        )
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            user_id,
                            title.strip(),
                            content.strip(),
                            location.strip()
                        )
                    )

                    st.success(
                        "Memory saved."
                    )

                    st.rerun()

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    search = st.text_input(
        "🔍 Search Memories"
    )

    if search.strip():

        rows = execute(
            """
            SELECT *
            FROM memories
            WHERE user_id=?
            AND
            (
                title LIKE ?
                OR content LIKE ?
                OR location LIKE ?
            )
            ORDER BY created_at DESC
            """,
            (
                user_id,
                f"%{search}%",
                f"%{search}%",
                f"%{search}%"
            ),
            fetch=True
        )

    else:

        rows = execute(
            """
            SELECT *
            FROM memories
            WHERE user_id=?
            ORDER BY created_at DESC
            """,
            (user_id,),
            fetch=True
        )

    if not rows:

        st.info(
            "No memories found."
        )

        return

    # -----------------------------------------------------
    # Display Memories
    # -----------------------------------------------------

    for memory in rows:

        with st.container(
            border=True
        ):

            st.markdown(
                f"**{memory['title']}**"
            )

            st.write(
                memory["content"]
            )

            if memory["location"]:

                st.info(
                    f"📍 {memory['location']}"
                )

            if st.button(
                "🗑️ Delete",
                key=f"del_memory_{memory['id']}"
            ):

                execute(
                    """
                    DELETE FROM memories
                    WHERE id=?
                    AND user_id=?
                    """,
                    (
                        memory["id"],
                        user_id
                    )
                )

                st.rerun()