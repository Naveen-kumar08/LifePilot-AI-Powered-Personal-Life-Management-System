import streamlit as st

from datetime import date, datetime

from database import execute


# ============================================================
# REMINDERS PAGE
# ============================================================

def show_reminders():

    st.title("⏰ Reminders")

    st.caption(
        "Create reminders with date, time and alarm."
    )


    # ========================================================
    # ADD REMINDER
    # ========================================================

    st.subheader(
        "➕ Add New Reminder"
    )


    with st.form(
        "add_reminder_form",
        clear_on_submit=True
    ):

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = st.text_input(
            "Reminder Title",
            placeholder="Example: Submit assignment"
        )


        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        description = st.text_area(
            "Description",
            placeholder="Additional details..."
        )


        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        reminder_date = st.date_input(
            "📅 Date",
            value=date.today()
        )


        # ----------------------------------------------------
        # TIME
        # ----------------------------------------------------

        col1, col2 = st.columns(
            [2, 1]
        )


        with col1:

            reminder_time = st.time_input(
                "⏰ Time",
                value=datetime.now().time().replace(
                    second=0,
                    microsecond=0
                )
            )


        with col2:

            am_pm = st.selectbox(
                "AM / PM",
                [
                    "AM",
                    "PM"
                ]
            )


        # ----------------------------------------------------
        # ALARM
        # ----------------------------------------------------

        alarm_enabled = st.checkbox(
            "🔔 Enable Alarm",
            value=True
        )


        # ----------------------------------------------------
        # SUBMIT
        # ----------------------------------------------------

        submitted = st.form_submit_button(
            "➕ Add Reminder",
            use_container_width=True
        )


        # ====================================================
        # SAVE
        # ====================================================

        if submitted:

            if not title.strip():

                st.error(
                    "Please enter a reminder title."
                )

            else:

                # --------------------------------------------
                # Convert selected time to 24-hour format
                # --------------------------------------------

                hour = reminder_time.hour

                minute = reminder_time.minute


                if am_pm == "AM":

                    if hour == 12:

                        hour = 0

                else:

                    if hour != 12:

                        hour += 12


                time_string = (
                    f"{hour:02d}:{minute:02d}"
                )


                # --------------------------------------------
                # Date string
                # --------------------------------------------

                date_string = (
                    reminder_date.strftime(
                        "%Y-%m-%d"
                    )
                )


                # --------------------------------------------
                # Insert
                # --------------------------------------------

                execute(
                    """
                    INSERT INTO reminders
                    (
                        user_id,
                        title,
                        description,
                        reminder_date,
                        reminder_time,
                        alarm_enabled,
                        status
                    )
                    VALUES
                    (
                        ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        st.session_state.user_id,
                        title.strip(),
                        description.strip(),
                        date_string,
                        time_string,
                        1 if alarm_enabled else 0,
                        "Pending"
                    )
                )


                st.success(
                    "✅ Reminder added successfully!"
                )


                st.rerun()


    st.divider()


    # ========================================================
    # FETCH REMINDERS
    # ========================================================

    reminders = execute(
        """
        SELECT
            id,
            title,
            description,
            reminder_date,
            reminder_time,
            alarm_enabled,
            status
        FROM reminders
        WHERE user_id = ?
        ORDER BY
            reminder_date ASC,
            reminder_time ASC
        """,
        (
            st.session_state.user_id,
        ),
        fetch=True,
        fetchone=False,
        commit=False
    )


    # ========================================================
    # NO REMINDERS
    # ========================================================

    if not reminders:

        st.info(
            "📭 No reminders yet. "
            "Create your first reminder above."
        )

        return


    # ========================================================
    # TODAY
    # ========================================================

    today_string = (
        date.today().strftime(
            "%Y-%m-%d"
        )
    )


    today_reminders = []

    upcoming_reminders = []

    completed_reminders = []


    for reminder in reminders:

        if reminder["status"] == "Completed":

            completed_reminders.append(
                reminder
            )

        elif reminder["reminder_date"] == today_string:

            today_reminders.append(
                reminder
            )

        else:

            upcoming_reminders.append(
                reminder
            )


    # ========================================================
    # FORMAT TIME
    # ========================================================

    def format_time(
        time_string
    ):

        try:

            parsed_time = datetime.strptime(
                time_string,
                "%H:%M"
            )

            return parsed_time.strftime(
                "%I:%M %p"
            ).lstrip("0")

        except Exception:

            return time_string


    # ========================================================
    # DISPLAY REMINDER
    # ========================================================

    def display_reminder(
        reminder
    ):

        reminder_id = reminder["id"]

        title = reminder["title"]

        description = (
            reminder["description"]
            or ""
        )

        reminder_date_value = (
            reminder["reminder_date"]
        )

        reminder_time_value = (
            reminder["reminder_time"]
        )

        alarm = reminder["alarm_enabled"]

        status = reminder["status"]


        # ----------------------------------------------------
        # Card
        # ----------------------------------------------------

        with st.container(
            border=True
        ):

            col1, col2 = st.columns(
                [4, 1]
            )


            with col1:

                if status == "Completed":

                    st.markdown(
                        f"### ✅ ~~{title}~~"
                    )

                else:

                    st.markdown(
                        f"### ⏰ {title}"
                    )


                if description:

                    st.write(
                        description
                    )


                # --------------------------------------------
                # Date
                # --------------------------------------------

                st.write(
                    f"📅 **Date:** "
                    f"{reminder_date_value}"
                )


                # --------------------------------------------
                # Time
                # --------------------------------------------

                st.write(
                    f"⏰ **Time:** "
                    f"{format_time(reminder_time_value)}"
                )


                # --------------------------------------------
                # Alarm
                # --------------------------------------------

                if alarm:

                    st.success(
                        "🔔 Alarm ON"
                    )

                else:

                    st.warning(
                        "🔕 Alarm OFF"
                    )


            with col2:

                # --------------------------------------------
                # Complete
                # --------------------------------------------

                if status != "Completed":

                    if st.button(
                        "✅ Done",
                        key=f"done_{reminder_id}",
                        use_container_width=True
                    ):

                        execute(
                            """
                            UPDATE reminders
                            SET status = 'Completed'
                            WHERE id = ?
                            AND user_id = ?
                            """,
                            (
                                reminder_id,
                                st.session_state.user_id
                            )
                        )

                        st.rerun()


                # --------------------------------------------
                # Delete
                # --------------------------------------------

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{reminder_id}",
                    use_container_width=True
                ):

                    execute(
                        """
                        DELETE FROM reminders
                        WHERE id = ?
                        AND user_id = ?
                        """,
                        (
                            reminder_id,
                            st.session_state.user_id
                        )
                    )

                    st.rerun()


    # ========================================================
    # TODAY
    # ========================================================

    st.subheader(
        "📌 Today's Reminders"
    )


    if today_reminders:

        for reminder in today_reminders:

            display_reminder(
                reminder
            )

    else:

        st.info(
            "No reminders scheduled for today."
        )


    # ========================================================
    # UPCOMING
    # ========================================================

    st.subheader(
        "📆 Upcoming Reminders"
    )


    if upcoming_reminders:

        for reminder in upcoming_reminders:

            display_reminder(
                reminder
            )

    else:

        st.info(
            "No upcoming reminders."
        )


    # ========================================================
    # COMPLETED
    # ========================================================

    if completed_reminders:

        with st.expander(
            "✅ Completed Reminders"
        ):

            for reminder in completed_reminders:

                display_reminder(
                    reminder
                )