import streamlit as st
import hashlib
import sqlite3

from database import execute


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    """
    Convert password into SHA-256 hash.
    """

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# VERIFY PASSWORD
# ============================================================

def verify_password(password, password_hash):
    """
    Check whether entered password matches stored hash.
    """

    return hash_password(password) == password_hash


# ============================================================
# SESSION LOGIN
# ============================================================

def login_user(user):
    """
    Store logged-in user information in Streamlit session.
    """

    st.session_state.user_id = user["id"]

    st.session_state.user_name = user["name"]

    st.session_state.user_email = user["email"]


# ============================================================
# LOGOUT
# ============================================================

def logout():
    """
    Logout current user.
    """

    st.session_state.user_id = None

    st.session_state.user_name = None

    st.session_state.user_email = None


# ============================================================
# REGISTER USER
# ============================================================

def register_user(name, email, password):

    name = name.strip()

    email = email.strip().lower()

    password = password.strip()


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not name:

        return False, "Please enter your name."


    if not email:

        return False, "Please enter your email."


    if not password:

        return False, "Please enter a password."


    if len(password) < 6:

        return False, "Password must contain at least 6 characters."


    # --------------------------------------------------------
    # CHECK EXISTING USER
    # --------------------------------------------------------

    existing_user = execute(
        """
        SELECT id
        FROM users
        WHERE email = ?
        """,
        (email,),
        fetchone=True,
        commit=False
    )


    if existing_user:

        return False, "An account with this email already exists."


    # --------------------------------------------------------
    # HASH PASSWORD
    # --------------------------------------------------------

    password_hash = hash_password(password)


    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    try:

        execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash
            )
            VALUES
            (
                ?,
                ?,
                ?
            )
            """,
            (
                name,
                email,
                password_hash
            )
        )

        return True, "Registration successful. You can now login."


    except sqlite3.IntegrityError:

        return False, "This email is already registered."


    except Exception as e:

        return False, f"Registration failed: {e}"


# ============================================================
# LOGIN USER
# ============================================================

def login_user_with_credentials(email, password):

    email = email.strip().lower()


    # --------------------------------------------------------
    # GET USER
    # --------------------------------------------------------

    user = execute(
        """
        SELECT
            id,
            name,
            email,
            password_hash
        FROM users
        WHERE email = ?
        """,
        (email,),
        fetchone=True,
        commit=False
    )


    if user is None:

        return False, "Invalid email or password."


    # --------------------------------------------------------
    # VERIFY PASSWORD
    # --------------------------------------------------------

    stored_hash = user["password_hash"]


    if not stored_hash:

        return False, "This account does not have a valid password."


    if not verify_password(
        password,
        stored_hash
    ):

        return False, "Invalid email or password."


    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    login_user(user)

    return True, "Login successful."


# ============================================================
# AUTHENTICATION UI
# ============================================================

def show_auth():

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:30px 0 10px 0;
        ">

        <h1>🚀 LifePilot</h1>

        <p style="
            font-size:18px;
            color:gray;
        ">
        Your Personal Life Admin Assistant
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # LOGIN / REGISTER TABS
    # ========================================================

    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "📝 Register"
        ]
    )


    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.subheader(
            "Welcome Back 👋"
        )

        email = st.text_input(
            "Email",
            key="login_email",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password",
            placeholder="Enter your password"
        )


        if st.button(
            "🔐 Login",
            use_container_width=True,
            type="primary"
        ):

            if not email or not password:

                st.warning(
                    "Please enter both email and password."
                )

            else:

                success, message = login_user_with_credentials(
                    email,
                    password
                )


                if success:

                    st.success(message)

                    st.rerun()

                else:

                    st.error(message)


    # ========================================================
    # REGISTER
    # ========================================================

    with register_tab:

        st.subheader(
            "Create Your LifePilot Account"
        )

        name = st.text_input(
            "Full Name",
            key="register_name",
            placeholder="Enter your name"
        )

        email = st.text_input(
            "Email",
            key="register_email",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password",
            placeholder="Minimum 6 characters"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm_password",
            placeholder="Re-enter your password"
        )


        if st.button(
            "📝 Create Account",
            use_container_width=True,
            type="primary"
        ):

            if password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = register_user(
                    name,
                    email,
                    password
                )


                if success:

                    st.success(message)

                    st.info(
                        "Please open the Login tab and login."
                    )

                else:

                    st.error(message)