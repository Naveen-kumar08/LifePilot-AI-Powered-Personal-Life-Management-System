from datetime import date

import streamlit as st

from database import execute


def show_warranties():

    user_id = st.session_state.user_id

    st.title("🛡️ Warranties")

    # -----------------------------------------------------
    # Add Warranty
    # -----------------------------------------------------

    with st.expander(
        "➕ Add Warranty",
        expanded=True
    ):

        with st.form("add_warranty"):

            product = st.text_input(
                "Product Name"
            )

            purchase_date = st.date_input(
                "Purchase Date",
                value=date.today()
            )

            expiry = st.date_input(
                "Warranty Expiry",
                value=date.today()
            )

            price = st.number_input(
                "Purchase Price (₹)",
                min_value=0.0,
                step=100.0
            )

            notes = st.text_area(
                "Notes"
            )

            submitted = st.form_submit_button(
                "Save Warranty"
            )

            if submitted:

                if not product.strip():

                    st.error(
                        "Enter product name."
                    )

                else:

                    execute(
                        """
                        INSERT INTO warranties
                        (
                            user_id,
                            product_name,
                            purchase_date,
                            warranty_expiry,
                            price,
                            notes
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            user_id,
                            product.strip(),
                            purchase_date.isoformat(),
                            expiry.isoformat(),
                            price,
                            notes
                        )
                    )

                    st.success(
                        "Warranty saved."
                    )

                    st.rerun()

    # -----------------------------------------------------
    # Get Warranties
    # -----------------------------------------------------

    rows = execute(
        """
        SELECT *
        FROM warranties
        WHERE user_id=?
        ORDER BY warranty_expiry
        """,
        (user_id,),
        fetch=True
    )

    if not rows:

        st.info(
            "No warranties recorded."
        )

        return

    today = date.today()

    # -----------------------------------------------------
    # Display
    # -----------------------------------------------------

    for warranty in rows:

        expiry = date.fromisoformat(
            warranty["warranty_expiry"]
        )

        days = (
            expiry - today
        ).days

        with st.container(
            border=True
        ):

            st.markdown(
                f"**{warranty['product_name']}**"
            )

            st.write(
                f"Purchase: {warranty['purchase_date']} | "
                f"Price: ₹{warranty['price']:,.2f}"
            )

            if days < 0:

                st.error(
                    f"Expired {abs(days)} days ago"
                )

            elif days <= 30:

                st.warning(
                    f"Expires in {days} days — "
                    f"{warranty['warranty_expiry']}"
                )

            else:

                st.success(
                    f"Valid for {days} more days"
                )

            if warranty["notes"]:

                st.caption(
                    warranty["notes"]
                )

            if st.button(
                "🗑️ Delete",
                key=f"del_warranty_{warranty['id']}"
            ):

                execute(
                    """
                    DELETE FROM warranties
                    WHERE id=?
                    AND user_id=?
                    """,
                    (
                        warranty["id"],
                        user_id
                    )
                )

                st.rerun()