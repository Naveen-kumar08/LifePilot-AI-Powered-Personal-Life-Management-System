from pathlib import Path
from datetime import date

import streamlit as st

from database import execute
from services.document_service import extract_text_from_pdf
from services.ai_service import extract_document_information


UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    exist_ok=True
)


# ---------------------------------------------------------
# Save File
# ---------------------------------------------------------

def save_uploaded_file(
    uploaded_file,
    user_id
):

    user_dir = UPLOAD_DIR / str(user_id)

    user_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_name = Path(
        uploaded_file.name
    ).name

    file_path = user_dir / safe_name

    file_path.write_bytes(
        uploaded_file.getbuffer()
    )

    return file_path


# ---------------------------------------------------------
# Delete Document
# ---------------------------------------------------------

def delete_document(
    document_id,
    user_id,
    file_path
):

    path = Path(file_path)

    try:

        if path.exists():

            path.unlink()

    except OSError:

        pass

    execute(
        """
        DELETE FROM documents
        WHERE id=?
        AND user_id=?
        """,
        (
            document_id,
            user_id
        )
    )


# ---------------------------------------------------------
# Create Reminder
# ---------------------------------------------------------

def create_reminder(
    user_id,
    title,
    description,
    reminder_date
):

    execute(
        """
        INSERT INTO reminders
        (
            user_id,
            title,
            description,
            reminder_date,
            repeat_type,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            title,
            description,
            reminder_date,
            "Once",
            "Pending"
        )
    )


# ---------------------------------------------------------
# Main Page
# ---------------------------------------------------------

def show_documents():

    user_id = st.session_state.user_id

    st.title("📄 Documents")

    st.caption(
        "Store, search, analyze and track "
        "important documents."
    )

    # =====================================================
    # Upload
    # =====================================================

    with st.expander(
        "➕ Upload Document",
        expanded=True
    ):

        with st.form(
            "upload_document_form"
        ):

            uploaded_file = st.file_uploader(
                "Choose a document",
                type=[
                    "pdf",
                    "txt",
                    "png",
                    "jpg",
                    "jpeg"
                ]
            )

            category = st.selectbox(
                "Category",
                [
                    "Identity",
                    "Education",
                    "Vehicle",
                    "Insurance",
                    "Finance",
                    "Work",
                    "Medical",
                    "Other"
                ]
            )

            has_expiry = st.checkbox(
                "This document has an expiry date"
            )

            expiry_date = None

            if has_expiry:

                expiry_date = st.date_input(
                    "Expiry Date",
                    value=date.today()
                )

            submitted = st.form_submit_button(
                "💾 Save Document",
                use_container_width=True
            )

            if submitted:

                if uploaded_file is None:

                    st.error(
                        "Please choose a document first."
                    )

                else:

                    try:

                        file_path = save_uploaded_file(
                            uploaded_file,
                            user_id
                        )

                        execute(
                            """
                            INSERT INTO documents
                            (
                                user_id,
                                name,
                                category,
                                file_path,
                                expiry_date
                            )
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                user_id,
                                uploaded_file.name,
                                category,
                                str(file_path),
                                (
                                    expiry_date.isoformat()
                                    if expiry_date
                                    else None
                                )
                            )
                        )

                        st.success(
                            "Document saved successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Could not save document: {e}"
                        )

    st.divider()

    # =====================================================
    # Search
    # =====================================================

    st.subheader(
        "🔍 Search Documents"
    )

    search = st.text_input(
        "Search by document name or category",
        placeholder="Example: insurance"
    )

    if search.strip():

        rows = execute(
            """
            SELECT *
            FROM documents
            WHERE user_id=?
            AND
            (
                name LIKE ?
                OR category LIKE ?
            )
            ORDER BY created_at DESC
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
            FROM documents
            WHERE user_id=?
            ORDER BY created_at DESC
            """,
            (user_id,),
            fetch=True
        )

    if not rows:

        st.info(
            "📭 No documents found."
        )

        return

    st.write(
        f"**{len(rows)} document(s) found**"
    )

    # =====================================================
    # Display
    # =====================================================

    for document in rows:

        document_id = document["id"]

        document_name = document["name"]

        category = document["category"]

        file_path = Path(
            document["file_path"]
        )

        expiry = document["expiry_date"]

        with st.container(
            border=True
        ):

            st.markdown(
                f"### 📄 {document_name}"
            )

            col1, col2, col3 = st.columns(3)

            # -------------------------------------------------
            # Category
            # -------------------------------------------------

            with col1:

                st.write(
                    f"**Category:** {category}"
                )

            # -------------------------------------------------
            # Expiry
            # -------------------------------------------------

            with col2:

                if expiry:

                    try:

                        expiry_obj = date.fromisoformat(
                            expiry
                        )

                        days_remaining = (
                            expiry_obj - date.today()
                        ).days

                        if days_remaining < 0:

                            st.error(
                                f"⛔ Expired on {expiry}"
                            )

                        elif days_remaining <= 7:

                            st.error(
                                f"🔴 Expires in "
                                f"{days_remaining} days"
                            )

                        elif days_remaining <= 30:

                            st.warning(
                                f"🟡 Expires in "
                                f"{days_remaining} days"
                            )

                        else:

                            st.success(
                                f"🟢 Expires in "
                                f"{days_remaining} days"
                            )

                    except ValueError:

                        st.write(
                            f"Expiry: {expiry}"
                        )

                else:

                    st.write(
                        "**Expiry:** Not set"
                    )

            # -------------------------------------------------
            # Download
            # -------------------------------------------------

            with col3:

                if file_path.exists():

                    st.download_button(
                        "⬇️ Download",
                        data=file_path.read_bytes(),
                        file_name=document_name,
                        key=f"download_{document_id}",
                        use_container_width=True
                    )

                else:

                    st.warning(
                        "File missing"
                    )

            # =================================================
            # AI PDF Analysis
            # =================================================

            if file_path.exists():

                extension = (
                    file_path.suffix.lower()
                )

                if extension == ".pdf":

                    with st.expander(
                        "🤖 AI Document Analysis"
                    ):

                        st.write(
                            "AI extracts document type, "
                            "person name, document number, "
                            "issue date and expiry date."
                        )

                        analyze = st.button(
                            "🔎 Analyze Document",
                            key=f"analyze_{document_id}",
                            use_container_width=True
                        )

                        if analyze:

                            # ---------------------------------
                            # Extract PDF Text
                            # ---------------------------------

                            with st.spinner(
                                "Reading PDF..."
                            ):

                                extracted_text = (
                                    extract_text_from_pdf(
                                        file_path
                                    )
                                )

                            if not extracted_text:

                                st.error(
                                    "Could not extract text."
                                )

                            else:

                                # -----------------------------
                                # AI Analysis
                                # -----------------------------

                                with st.spinner(
                                    "🤖 AI is analyzing..."
                                ):

                                    result = (
                                        extract_document_information(
                                            extracted_text[:12000]
                                        )
                                    )

                                # -----------------------------
                                # AI Error
                                # -----------------------------

                                if (
                                    not isinstance(
                                        result,
                                        dict
                                    )
                                    or "error" in result
                                ):

                                    if isinstance(
                                        result,
                                        dict
                                    ):

                                        error = result.get(
                                            "error",
                                            "Unknown AI error."
                                        )

                                    else:

                                        error = (
                                            "Invalid AI response."
                                        )

                                    st.error(error)

                                # -----------------------------
                                # Successful AI Response
                                # -----------------------------

                                else:

                                    st.success(
                                        "✅ Document analyzed."
                                    )

                                    info1, info2 = (
                                        st.columns(2)
                                    )

                                    with info1:

                                        st.write(
                                            "**Document Type**"
                                        )

                                        st.info(
                                            result.get(
                                                "document_type",
                                                ""
                                            )
                                            or "Not found"
                                        )

                                        st.write(
                                            "**Person Name**"
                                        )

                                        st.info(
                                            result.get(
                                                "person_name",
                                                ""
                                            )
                                            or "Not found"
                                        )

                                        st.write(
                                            "**Document Number**"
                                        )

                                        st.info(
                                            result.get(
                                                "document_number",
                                                ""
                                            )
                                            or "Not found"
                                        )

                                    with info2:

                                        st.write(
                                            "**Issue Date**"
                                        )

                                        st.info(
                                            result.get(
                                                "issue_date",
                                                ""
                                            )
                                            or "Not found"
                                        )

                                        ai_expiry = result.get(
                                            "expiry_date",
                                            ""
                                        )

                                        st.write(
                                            "**Expiry Date**"
                                        )

                                        st.info(
                                            ai_expiry or "Not found"
                                        )

                                    st.write(
                                        "**Important Information**"
                                    )

                                    st.write(
                                        result.get(
                                            "important_information",
                                            ""
                                        )
                                        or
                                        "No additional information."
                                    )

                                    # =========================
                                    # Reminder
                                    # =========================

                                    if ai_expiry:

                                        st.divider()

                                        st.subheader(
                                            "🔔 Create Reminder"
                                        )

                                        try:

                                            parsed_expiry = (
                                                date.fromisoformat(
                                                    ai_expiry
                                                )
                                            )

                                            reminder_title = (
                                                st.text_input(
                                                    "Reminder Title",
                                                    value=(
                                                        f"{result.get('document_type', 'Document')} "
                                                        f"expiry"
                                                    ),
                                                    key=(
                                                        f"title_{document_id}"
                                                    )
                                                )
                                            )

                                            reminder_description = (
                                                st.text_area(
                                                    "Reminder Description",
                                                    value=(
                                                        f"{document_name} "
                                                        f"expires on "
                                                        f"{ai_expiry}."
                                                    ),
                                                    key=(
                                                        f"description_{document_id}"
                                                    )
                                                )
                                            )

                                            if st.button(
                                                "🔔 Create Reminder",
                                                key=(
                                                    f"reminder_{document_id}"
                                                ),
                                                use_container_width=True
                                            ):

                                                create_reminder(
                                                    user_id,
                                                    reminder_title,
                                                    reminder_description,
                                                    parsed_expiry.isoformat()
                                                )

                                                st.success(
                                                    "Reminder created successfully!"
                                                )

                                        except ValueError:

                                            st.warning(
                                                "AI expiry date is not "
                                                "in YYYY-MM-DD format."
                                            )

                                    # =========================
                                    # Extracted Text
                                    # =========================

                                    with st.expander(
                                        "📑 View Extracted PDF Text"
                                    ):

                                        st.text_area(
                                            "PDF Text",
                                            extracted_text,
                                            height=250,
                                            key=(
                                                f"text_{document_id}"
                                            )
                                        )

                else:

                    st.caption(
                        "AI analysis is currently "
                        "available for PDF files."
                    )

            # =================================================
            # Delete
            # =================================================

            st.divider()

            if st.button(
                "🗑️ Delete",
                key=f"delete_{document_id}",
                use_container_width=True
            ):

                delete_document(
                    document_id,
                    user_id,
                    file_path
                )

                st.success(
                    "Document deleted."
                )

                st.rerun()