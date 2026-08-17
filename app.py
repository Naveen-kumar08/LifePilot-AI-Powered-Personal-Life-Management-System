import streamlit as st

import streamlit.components.v1 as components

import os
import base64
import json

from datetime import datetime


# ============================================================
# LIFE PILOT
# MAIN APPLICATION
# ============================================================


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="LifePilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DATABASE
# ============================================================

from database import init_db, execute

init_db()


# ============================================================
# AUTH
# ============================================================

from auth import show_auth, logout


# ============================================================
# SESSION STATE
# ============================================================

if "user_id" not in st.session_state:

    st.session_state.user_id = None


if "user_name" not in st.session_state:

    st.session_state.user_name = None


if "user_email" not in st.session_state:

    st.session_state.user_email = None


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    section[data-testid="stSidebar"] {
        min-width: 260px;
        max-width: 280px;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    input,
    textarea {
        border-radius: 8px !important;
    }

    .lifepilot-footer {
        text-align: center;
        padding: 30px 0 10px 0;
        color: gray;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# GET GLOBAL REMINDERS
# ============================================================

def get_global_reminders():

    if not st.session_state.user_id:

        return []


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    try:

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
            AND reminder_date = ?
            AND status = 'Pending'
            AND alarm_enabled = 1
            ORDER BY reminder_time ASC
            """,
            (
                st.session_state.user_id,
                today
            ),
            fetch=True,
            fetchone=False,
            commit=False
        )


        result = []


        for reminder in reminders:

            result.append(
                {
                    "id": reminder["id"],
                    "title": reminder["title"] or "Reminder",
                    "description": (
                        reminder["description"]
                        or ""
                    ),
                    "date": (
                        reminder["reminder_date"]
                    ),
                    "time": (
                        reminder["reminder_time"]
                    )
                }
            )


        return result


    except Exception as error:

        print(
            "Global reminder error:",
            error
        )

        return []


# ============================================================
# GLOBAL ALARM SYSTEM
# ============================================================

def global_alarm_system():

    if not st.session_state.user_id:

        return


    reminders = get_global_reminders()


    # ========================================================
    # ALARM FILE
    # ========================================================

    project_folder = os.path.dirname(
        os.path.abspath(__file__)
    )


    alarm_file = os.path.join(
        project_folder,
        "assets",
        "alarm.wav"
    )


    audio_base64 = ""


    if os.path.exists(
        alarm_file
    ):

        try:

            with open(
                alarm_file,
                "rb"
            ) as audio:

                audio_base64 = (
                    base64.b64encode(
                        audio.read()
                    ).decode(
                        "utf-8"
                    )
                )

        except Exception as error:

            print(
                "Could not read alarm.wav:",
                error
            )


    # ========================================================
    # JSON
    # ========================================================

    reminders_json = json.dumps(
        reminders
    )


    # ========================================================
    # HTML / JAVASCRIPT
    #
    # DO NOT convert this to an f-string.
    # ========================================================

    html = """
<!DOCTYPE html>

<html>

<head>

<style>

body {

    margin: 0;

    padding: 0;

    background: transparent;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

}


/* ==========================================================
   ENABLE BUTTON
========================================================== */

#enableBox {

    position: fixed;

    right: 20px;

    bottom: 20px;

    width: 320px;

    padding: 18px;

    background: white;

    border-radius: 15px;

    border: 2px solid #4f46e5;

    box-shadow:
        0 8px 30px
        rgba(0,0,0,0.25);

    z-index: 999998;

    display: none;

}


#enableButton {

    width: 100%;

    padding: 12px;

    border: none;

    border-radius: 8px;

    background: #4f46e5;

    color: white;

    font-size: 15px;

    font-weight: bold;

    cursor: pointer;

}


/* ==========================================================
   ALARM
========================================================== */

#alarmBox {

    position: fixed;

    top: 20px;

    right: 20px;

    width: 390px;

    padding: 25px;

    background: white;

    border: 4px solid red;

    border-radius: 18px;

    box-shadow:
        0 10px 50px
        rgba(255,0,0,0.50);

    z-index: 999999;

    display: none;

    text-align: center;

    animation:
        pulse 1s infinite;

}


@keyframes pulse {

    0% {

        transform:
            scale(1);

    }

    50% {

        transform:
            scale(1.04);

    }

    100% {

        transform:
            scale(1);

    }

}


.icon {

    font-size: 55px;

}


.heading {

    font-size: 30px;

    font-weight: bold;

    color: red;

    margin-bottom: 10px;

}


.title {

    font-size: 23px;

    font-weight: bold;

    margin-bottom: 10px;

}


.description {

    color: #555;

    margin-bottom: 10px;

}


.time {

    color: #777;

    margin-bottom: 20px;

}


#stopButton {

    width: 100%;

    padding: 14px;

    border: none;

    border-radius: 10px;

    background: red;

    color: white;

    font-size: 17px;

    font-weight: bold;

    cursor: pointer;

}


#stopButton:hover {

    background: darkred;

}


#status {

    margin-top: 10px;

    font-size: 13px;

    color: #666;

}

</style>

</head>


<body>


<!-- ========================================================
     ENABLE NOTIFICATIONS
======================================================== -->

<div id="enableBox">

    <h3>
        🔔 Enable LifePilot Alarm
    </h3>

    <p>
        Click this button once to allow
        LifePilot to play reminder alarms
        and browser notifications.
    </p>

    <button
        id="enableButton"
        onclick="enableAlarm()">

        🔔 Enable Alarm & Notifications

    </button>

</div>


<!-- ========================================================
     ALARM POPUP
======================================================== -->

<div id="alarmBox">

    <div class="icon">
        🚨
    </div>

    <div class="heading">
        REMINDER!
    </div>

    <div
        id="alarmTitle"
        class="title">
    </div>

    <div
        id="alarmDescription"
        class="description">
    </div>

    <div
        id="alarmTime"
        class="time">
    </div>

    <audio
        id="alarmAudio"
        loop
        preload="auto">

        <source
            id="alarmSource"
            type="audio/wav">

    </audio>


    <button
        id="stopButton"
        onclick="stopAlarm()">

        🔕 STOP ALARM

    </button>


    <div id="status">
        🔊 Waiting...
    </div>

</div>


<script>


// ==========================================================
// PYTHON DATA
// ==========================================================

const reminders =
    __REMINDERS__;


const audioData =
    "__AUDIO__";


// ==========================================================
// VARIABLES
// ==========================================================

let activeReminderId =
    null;


let audioUnlocked =
    false;


// ==========================================================
// AUDIO
// ==========================================================

const audio =
    document.getElementById(
        "alarmAudio"
    );


const audioSource =
    document.getElementById(
        "alarmSource"
    );


if (
    audioData &&
    audioData.length > 0
) {

    audioSource.src =
        "data:audio/wav;base64,"
        +
        audioData;

    audio.load();

}


// ==========================================================
// ENABLE ALARM
// ==========================================================

function enableAlarm() {

    // ------------------------------------------------------
    // Notification permission
    // ------------------------------------------------------

    if (
        "Notification"
        in window
    ) {

        Notification.requestPermission();

    }


    // ------------------------------------------------------
    // Unlock audio
    // ------------------------------------------------------

    if (
        audioData
    ) {

        audio.muted = true;

        const promise =
            audio.play();


        if (
            promise !== undefined
        ) {

            promise
                .then(
                    function() {

                        audio.pause();

                        audio.currentTime = 0;

                        audio.muted = false;

                        audioUnlocked = true;

                    }
                )
                .catch(
                    function(error) {

                        console.log(
                            "Audio unlock:",
                            error
                        );

                    }
                );

        }

    }


    document.getElementById(
        "enableBox"
    ).style.display =
        "none";

}


// ==========================================================
// SHOW DESKTOP NOTIFICATION
// ==========================================================

function showNotification(
    reminder
) {

    if (
        !("Notification" in window)
    ) {

        return;

    }


    if (
        Notification.permission !==
        "granted"
    ) {

        return;

    }


    try {

        const notification =
            new Notification(
                "🚨 LifePilot Reminder",
                {
                    body:
                        reminder.title
                        +
                        (
                            reminder.description
                            ?
                            "\n"
                            +
                            reminder.description
                            :
                            ""
                        ),

                    requireInteraction:
                        true
                }
            );


        notification.onclick =
            function() {

                window.focus();

                notification.close();

            };

    }
    catch(error) {

        console.log(
            error
        );

    }

}


// ==========================================================
// PLAY ALARM
// ==========================================================

function playAlarm() {

    if (
        !audioData
    ) {

        document.getElementById(
            "status"
        ).innerText =
            "⚠️ alarm.wav not found.";

        return;

    }


    try {

        audio.currentTime = 0;

        audio.loop = true;


        const promise =
            audio.play();


        if (
            promise !== undefined
        ) {

            promise
                .then(
                    function() {

                        document.getElementById(
                            "status"
                        ).innerText =
                            "🔊 Alarm playing...";

                    }
                )
                .catch(
                    function(error) {

                        console.log(
                            "Audio blocked:",
                            error
                        );


                        document.getElementById(
                            "status"
                        ).innerText =
                            "🔇 Click Enable Alarm first.";

                    }
                );

        }

    }
    catch(error) {

        console.log(
            error
        );

    }

}


// ==========================================================
// SHOW ALARM
// ==========================================================

function showAlarm(
    reminder
) {

    // ------------------------------------------------------
    // Don't repeatedly show same alarm
    // ------------------------------------------------------

    if (
        activeReminderId ===
        reminder.id
    ) {

        return;

    }


    activeReminderId =
        reminder.id;


    // ------------------------------------------------------
    // Title
    // ------------------------------------------------------

    document.getElementById(
        "alarmTitle"
    ).innerText =
        reminder.title;


    // ------------------------------------------------------
    // Description
    // ------------------------------------------------------

    document.getElementById(
        "alarmDescription"
    ).innerText =
        reminder.description
        ||
        "You have a reminder.";


    // ------------------------------------------------------
    // Time
    // ------------------------------------------------------

    document.getElementById(
        "alarmTime"
    ).innerText =
        "⏰ "
        +
        reminder.time;


    // ------------------------------------------------------
    // Display
    // ------------------------------------------------------

    document.getElementById(
        "alarmBox"
    ).style.display =
        "block";


    // ------------------------------------------------------
    // Notification
    // ------------------------------------------------------

    showNotification(
        reminder
    );


    // ------------------------------------------------------
    // Sound
    // ------------------------------------------------------

    playAlarm();

}


// ==========================================================
// STOP ALARM
// ==========================================================

function stopAlarm() {

    try {

        audio.pause();

        audio.currentTime = 0;

    }
    catch(error) {

        console.log(
            error
        );

    }


    document.getElementById(
        "alarmBox"
    ).style.display =
        "none";


    document.getElementById(
        "status"
    ).innerText =
        "🔕 Alarm stopped.";


    activeReminderId =
        null;

}


// ==========================================================
// CURRENT DATE
// ==========================================================

function getDate() {

    const now =
        new Date();


    const year =
        now.getFullYear();


    const month =
        String(
            now.getMonth() + 1
        ).padStart(
            2,
            "0"
        );


    const day =
        String(
            now.getDate()
        ).padStart(
            2,
            "0"
        );


    return (
        year
        +
        "-"
        +
        month
        +
        "-"
        +
        day
    );

}


// ==========================================================
// CURRENT TIME
// ==========================================================

function getTime() {

    const now =
        new Date();


    const hour =
        String(
            now.getHours()
        ).padStart(
            2,
            "0"
        );


    const minute =
        String(
            now.getMinutes()
        ).padStart(
            2,
            "0"
        );


    return (
        hour
        +
        ":"
        +
        minute
    );

}


// ==========================================================
// CHECK REMINDERS
// ==========================================================

function checkReminders() {

    if (
        !reminders
        ||
        reminders.length === 0
    ) {

        return;

    }


    const today =
        getDate();


    const currentTime =
        getTime();


    reminders.forEach(
        function(reminder) {

            if (
                reminder.date ===
                today
                &&
                reminder.time ===
                currentTime
            ) {

                showAlarm(
                    reminder
                );

            }

        }
    );

}


// ==========================================================
// NOTIFICATION PERMISSION
// ==========================================================

function checkPermission() {

    if (
        !("Notification" in window)
    ) {

        return;

    }


    if (
        Notification.permission ===
        "default"
    ) {

        document.getElementById(
            "enableBox"
        ).style.display =
            "block";

    }

}


// ==========================================================
// INITIALIZATION
// ==========================================================

checkPermission();

checkReminders();


// ==========================================================
// CHECK EVERY SECOND
// ==========================================================

setInterval(
    checkReminders,
    1000
);


</script>


</body>

</html>
"""


    # ========================================================
    # INSERT DATA
    #
    # IMPORTANT:
    # .replace() is used.
    # NO f-string.
    # ========================================================

    html = html.replace(
        "__REMINDERS__",
        reminders_json
    )


    html = html.replace(
        "__AUDIO__",
        audio_base64
    )


    # ========================================================
    # RENDER GLOBAL ALARM
    # ========================================================

    components.html(
        html,
        height=10,
        scrolling=False
    )


# ============================================================
# LOGIN SCREEN
# ============================================================

if st.session_state.user_id is None:

    st.markdown(
        """
        <style>

        section[data-testid="stSidebar"] {
            display: none;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    show_auth()


    st.stop()


# ============================================================
# GLOBAL ALARM
#
# THIS IS BEFORE PAGE ROUTING.
#
# Therefore it is loaded regardless of which
# sidebar option is selected.
# ============================================================

global_alarm_system()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "# 🚀 LIFEPILOT"
    )


    st.caption(
        "Personal Life Admin Assistant"
    )


    st.divider()


    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    st.markdown(
        "### 👋 Hello, "
        +
        str(
            st.session_state.user_name
            or "User"
        )
    )


    if st.session_state.user_email:

        st.caption(
            st.session_state.user_email
        )


    st.divider()


    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    st.markdown(
        "### Navigation"
    )


    selected_page = st.radio(
        "Select a module",

        [
            "🏠 Dashboard",
            "✅ Tasks",
            "⏰ Reminders",
            "📄 Documents",
            "💰 Expenses",
            "🛡️ Warranties",
            "📝 Notes",
            "🧠 Memories"
        ],

        index=0,

        label_visibility="collapsed"
    )


    st.divider()


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    st.markdown(
        "### 🔔 Alarm System"
    )


    st.caption(
        "Global reminders are active."
    )


    st.caption(
        "You can use any module while waiting "
        "for an alarm."
    )


    st.divider()


    # --------------------------------------------------------
    # APP INFO
    # --------------------------------------------------------

    st.caption(
        "LifePilot v1.0"
    )


    st.caption(
        "Manage your life in one place."
    )


    st.divider()


    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        logout()

        st.rerun()


# ============================================================
# PAGE ROUTING
# ============================================================

if selected_page == "🏠 Dashboard":

    from views.dashboard import show_dashboard

    show_dashboard()


elif selected_page == "✅ Tasks":

    from views.tasks import show_tasks

    show_tasks()


elif selected_page == "⏰ Reminders":

    from views.reminders import show_reminders

    show_reminders()


elif selected_page == "📄 Documents":

    from views.documents import show_documents

    show_documents()


elif selected_page == "💰 Expenses":

    from views.expenses import show_expenses

    show_expenses()


elif selected_page == "🛡️ Warranties":

    from views.warranties import show_warranties

    show_warranties()


elif selected_page == "📝 Notes":

    from views.notes import show_notes

    show_notes()


elif selected_page == "🧠 Memories":

    from views.memories import show_memories

    show_memories()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="lifepilot-footer">

        🚀 LifePilot —
        Your Personal Life Admin Assistant

    </div>
    """,
    unsafe_allow_html=True
)