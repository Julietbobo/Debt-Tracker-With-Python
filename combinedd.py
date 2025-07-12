import streamlit as st
import pandas as pd
import mysql.connector
import bcrypt
import time

# ------------------------------
# 🔁 Page switching helpers
def switch_to_register():
    st.session_state.page = "register"

def switch_to_login():
    st.session_state.page = "login"

def switch_to_dashboard():
    st.session_state.page = "dashboard"

# ------------------------------
# 🔐 Login Page
def login_page():
    st.title("🔐 Login")

    phone = st.text_input("Phone Number", key="login_phone")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        try:
            conn = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                database=st.secrets["mysql"]["database"]
            )
            cur = conn.cursor()
            cur.execute("SELECT first_name, password FROM users WHERE phone_number = %s", (phone,))
            result = cur.fetchone()

            if result:
                first_name, stored_hashed_pw = result
                if bcrypt.checkpw(password.encode(), stored_hashed_pw.encode()):
                    st.success(f"Welcome back, {first_name}!")
                    st.session_state.is_logged_in = True
                    st.session_state.user = {"first_name": first_name}
                    switch_to_dashboard()
                    st.rerun()
                else:
                    st.error("Incorrect password")
            else:
                st.warning("User not found. Redirecting to registration...")
                switch_to_register()
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            cur.close()
            conn.close()

    st.button("New user? Register here", on_click=switch_to_register)

# ------------------------------
# 📝 Registration Page
def registration_page():
    st.title("📝 Register")
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name", key="reg_first_name")
    with col2:
        last_name = st.text_input("Last Name", key="reg_last_name")

    phone = st.text_input("Phone Number", key="reg_phone")
    password = st.text_input("Password", type="password", key="reg_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")

    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match")
            return

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        try:
            conn = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                database=st.secrets["mysql"]["database"]
            )
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (first_name, last_name, phone_number, password)
                VALUES (%s, %s, %s, %s)
            """, (first_name, last_name, phone, hashed_pw))
            conn.commit()
            st.success("Account created successfully!")
            switch_to_login()
            st.rerun()
        except mysql.connector.IntegrityError:
            st.error("Phone number already registered.")
        except Exception as e:
            st.error(f"Database error: {e}")
        finally:
            cur.close()
            conn.close()

    st.button("Back to Login", on_click=switch_to_login)

# ------------------------------
# 📊 Dashboard
def dashboard_page():
    st.header("📊 Debt Dashboard")
    user = st.session_state.get("user", {})
    st.markdown(f"Welcome, **{user.get('first_name', 'User')}**")

    try:
        conn = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                database=st.secrets["mysql"]["database"]
        )
        cur = conn.cursor()
        cur.execute("SELECT SUM(unpaid_amount) FROM debts")
        total_debt = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM debts WHERE paid_amount > 0")
        debtors_paid = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM debts WHERE unpaid_amount > 0")
        debtors_owing = cur.fetchone()[0]
    except Exception as e:
        st.error(f"Error fetching dashboard data: {e}")
        return
    finally:
        cur.close()
        conn.close()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Debt", f"KSh {total_debt:,.0f}")
    col2.metric("Debtors Paid", debtors_paid)
    col3.metric("Debtors Owing", debtors_owing)

# ------------------------------
# ➕ Add Debtor
def add_debtor_page():
    st.header("➕ Record New Debt")
    date = st.date_input("Date of Transaction")
    col1, col2 = st.columns(2)
    customer_name = col1.text_input("Customer Name")
    product = col2.text_input("Product Taken")
    col1, col2 = st.columns(2)
    total = col1.number_input("Total", min_value=0, step=1, format="%d")
    paid = col2.number_input("Amount Paid", min_value=0, max_value=total, step=1, format="%d")
    unpaid = total - paid
    st.info(f"🧾 Unpaid Amount: KSh {unpaid}")

    if st.button("Save Debt Record"):
        try:
            conn = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                database=st.secrets["mysql"]["database"]
            )
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO debts (customer_name, product, total, unpaid_amount, paid_amount, transaction_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (customer_name, product, total, unpaid, paid, date))
            conn.commit()
            st.success("Debt record saved successfully!")
        except Exception as e:
            st.error(f"Error saving record: {e}")
        finally:
            cur.close()
            conn.close()

# ------------------------------
# 📋 View Debtors
def view_debtors_page():
    st.header("📋 Recorded Debts")
    try:
        conn = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                database=st.secrets["mysql"]["database"]
        )
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT customer_name AS `Customer`, product AS `Product`, total AS `Total`,
                   unpaid_amount AS `Unpaid (KSh)`, paid_amount AS `Paid (KSh)`,
                   transaction_date AS `Date`
            FROM debts
            WHERE unpaid_amount > 0
            ORDER BY transaction_date DESC
        """)
        df = pd.DataFrame(cur.fetchall())
        if df.empty:
            st.info("No debt records found.")
        else:
            df.index = range(1, len(df) + 1)
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading data: {e}")
    finally:
        cur.close()
        conn.close()

# ------------------------------
# 💸 Record Payment
def record_payment_page():
    st.header("💸 Record a Payment")

    try:
        conn = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                database=st.secrets["mysql"]["database"]
        )
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT customer_name FROM debts")
        customers = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Error loading customers: {e}")
        return

    col1, col2 = st.columns(2)
    customer = col1.selectbox("Select Customer", customers)
    date = col2.date_input("Date of Payment")

    try:
        conn = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                database=st.secrets["mysql"]["database"]
        )
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, paid_amount, unpaid_amount
            FROM debts
            WHERE customer_name = %s AND unpaid_amount > 0
            ORDER BY transaction_date DESC
            LIMIT 1
        """, (customer,))
        debt = cur.fetchone()

        if debt:
            unpaid = int(debt["unpaid_amount"])
            payment = st.number_input("Amount Being Paid", min_value=1, max_value=unpaid, step=1, format="%d")
            if st.button("Apply Payment"):
                new_paid = debt["paid_amount"] + payment
                new_unpaid = debt["unpaid_amount"] - payment

                cur.execute("""
                    UPDATE debts SET paid_amount = %s, unpaid_amount = %s WHERE id = %s
                """, (new_paid, new_unpaid, debt["id"]))

                cur.execute("""
                    INSERT INTO payments (customer_name, payment_date, amount_paid, debt_id)
                    VALUES (%s, %s, %s, %s)
                """, (customer, date, payment, debt["id"]))

                conn.commit()
                st.success(f"Payment of KSh {payment} applied. New balance: KSh {new_unpaid}")
        else:
            st.warning("No unpaid debt found for this customer.")
    except Exception as e:
        st.error(f"Payment error: {e}")
    finally:
        cur.close()
        conn.close()

# ------------------------------
# 🧐 Main Controller
def main():
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False

    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        registration_page()
    elif st.session_state.is_logged_in:
        choice = st.sidebar.radio("🔍 Navigate", [
            "📊 Dashboard", "➕ Add Debtor", "📋 View Debtors", "💸 Record Payment", "🚪 Logout"])

        if choice == "📊 Dashboard":
            dashboard_page()
        elif choice == "➕ Add Debtor":
            add_debtor_page()
        elif choice == "📋 View Debtors":
            view_debtors_page()
        elif choice == "💸 Record Payment":
            record_payment_page()
        elif choice == "🚪 Logout":
            switch_to_login()
            st.session_state.is_logged_in = False
            st.session_state.user = {}
            st.rerun()
    else:
        st.warning("Please log in to access this page.")

main()
