from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from database import execute


CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Education",
    "Bills",
    "Entertainment",
    "Healthcare",
    "Other"
]


def show_expenses():

    user_id = st.session_state.user_id

    st.title("💰 Expenses")

    # -----------------------------------------------------
    # Add Expense
    # -----------------------------------------------------

    with st.expander(
        "➕ Add Expense",
        expanded=True
    ):

        with st.form("add_expense"):

            category = st.selectbox(
                "Category",
                CATEGORIES
            )

            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                step=10.0
            )

            description = st.text_input(
                "Description"
            )

            expense_date = st.date_input(
                "Date",
                value=date.today()
            )

            submitted = st.form_submit_button(
                "Add Expense"
            )

            if submitted:

                if amount <= 0:

                    st.error(
                        "Amount must be greater than zero."
                    )

                else:

                    execute(
                        """
                        INSERT INTO expenses
                        (
                            user_id,
                            category,
                            amount,
                            description,
                            expense_date
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            user_id,
                            category,
                            amount,
                            description,
                            expense_date.isoformat()
                        )
                    )

                    st.success(
                        "Expense added."
                    )

                    st.rerun()

    # -----------------------------------------------------
    # Get Expenses
    # -----------------------------------------------------

    rows = execute(
        """
        SELECT *
        FROM expenses
        WHERE user_id=?
        ORDER BY expense_date DESC
        """,
        (user_id,),
        fetch=True
    )

    data = [
        dict(row)
        for row in rows
    ]

    if not data:

        st.info(
            "No expenses recorded."
        )

        return

    df = pd.DataFrame(data)

    total = float(
        df["amount"].sum()
    )

    st.metric(
        "Total Recorded",
        f"₹{total:,.2f}"
    )

    # -----------------------------------------------------
    # Chart
    # -----------------------------------------------------

    summary = (
        df.groupby(
            "category",
            as_index=False
        )["amount"]
        .sum()
    )

    fig = px.pie(
        summary,
        names="category",
        values="amount",
        title="Spending by Category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------------------------------------
    # Table
    # -----------------------------------------------------

    st.dataframe(
        df[
            [
                "id",
                "expense_date",
                "category",
                "amount",
                "description"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # Delete
    # -----------------------------------------------------

    selected_id = st.number_input(
        "Expense ID to delete",
        min_value=0,
        step=1
    )

    if (
        st.button(
            "Delete Selected Expense"
        )
        and selected_id
    ):

        execute(
            """
            DELETE FROM expenses
            WHERE id=?
            AND user_id=?
            """,
            (
                int(selected_id),
                user_id
            )
        )

        st.success(
            "Expense deleted."
        )

        st.rerun()