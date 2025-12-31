# ============================================================
# Bank Management System (Single File Version)
# Streamlit + JSON
# Each section is labeled with the team member name.
# File name suggestion: bank_system.py
# Run: py -3.12 -m streamlit run final2.py
# ============================================================



# =========================================
# المكاتب المستخدمه في البروجيكت 
# =========================================
import streamlit as st
from datetime import datetime, date
import json
import os
import base64




# =========================================
# دي داله تحول الصوره ل Binary
# =========================================
def set_background(image_path: str):
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()




# =========================================
# استخدمنا css عشان نظبط شكل الصوره 
# =========================================
    st.markdown(
        f"""
    <style>
    /* background image */
    .stApp {{
        background-image: url("data:image/png;base64,{img}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )
st.write(
    "Welcome To The Bank. 👋 You can visit our website (https://bms-mufai.streamlit.app/)."
)



# ============================================================
# Database 
# ============================================================
DB_FILE = "database.json"
def load_database():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "accounts" not in data:
                data["accounts"] = {}
            if "history" not in data:
                data["history"] = []
            return data
    return {"accounts": {}, "history": []}


def save_database(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def add_history(db, action, account_id, amount=0, to_acc=None):
    db["history"].append(
        {
            "action": action,
            "account": account_id,
            "to_account": to_acc,
            "amount": float(amount),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )    




# ============================================================
#  محمد رافع
# منطق التحويل , نفس الحساب ,  
# ============================================================
class Account_Rafaa:
    def __init__(self, acc_id, owner, balance=0.0, status="Active"):
        self.acc_id = acc_id
        self.owner = owner
        self.balance = float(balance)
        self.status = status
        
    def is_active(self):
        return self.status == "Active"

    def can_receive(self):
        return self.status in ("Active", "Frozen")

    def __repr__(self):
        return f"{self.acc_id}:{self.balance:.2f}({self.status})"


class Bank_Rafaa:
    def __init__(self, db):
        self.db = db
        self.accounts = db["accounts"]

    def get(self, acc_id):
        return self.accounts.get(acc_id)

    def transfer(self, src, dst, amt):
        if src == dst:
            return False, "You can't transfer to the same account."

        s = self.get(src)
        r = self.get(dst)

        if not s or not r:
            return False, "One of the accounts does not exist."

        if amt <= 0:
            return False, "Amount must be greater than 0 LE."

        if s.get("status") != "Active":
            return False, f"Source account is not active ({s.get('status')})."

        if r.get("status") not in ("Active", "Frozen"):
            return (
                False,
                f"Reciver account does not accept transfers ({r.get('status')}).",
            )

        if s.get("balance", 0) < amt:
            return False, "Insufficient balance."

        
        s["balance"] -= float(amt)
        r["balance"] += float(amt)

        add_history(self.db, "Transfer", src, amt, to_acc=dst)
        return True, f"Transferred {amt:.2f} EGP from {src} to {dst}."


# ============================================================
# Author: مصطفى عيد
# صحه البيانات , انشاء , تحديث  , حفظ 
# ============================================================
def validate_name_eid(name: str) -> bool:
    return bool(name.strip()) and all(c.isalpha() or c.isspace() for c in name)


def validate_phone_eid(phone: str) -> bool:
    phone = str(phone).strip()
    if not phone.isdigit():
        return False
    if len(phone) != 11:
        return False
    if not phone.startswith(("010", "011", "012", "015")):
        return False
    return True


def generate_account_id_eid(db, start_from=1001) -> str:
    accounts = db.get("accounts", {})
    if not accounts:
        return str(start_from)

    numeric_ids = []
    for k in accounts.keys():
        try:
            numeric_ids.append(int(k))
        except ValueError:
            pass

    if not numeric_ids:
        return str(start_from)

    return str(max(numeric_ids) + 1)


def create_account_auto_id_eid(db, name, phone, national_id="", balance=50.0):
    if not validate_name_eid(name):
        return False, None, "Invalid name (letters and spaces only)."

    if not validate_phone_eid(phone):
        return (
            False,
            None,
            "Invalid phone number (Must begain with 010 | 011 | 012 | 015). ",
        )

    acc_id = generate_account_id_eid(db)

    db["accounts"][acc_id] = {
        "name": name,
        "phone": phone,
        "national_id": national_id,
        "balance": float(balance),
        "status": "Active",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    add_history(db, "Create", acc_id, amount=float(balance))
    return True, acc_id, "Account created successfully ✅"


def update_status_eid(db, acc_id, new_status):
    acc = db["accounts"].get(acc_id)
    if not acc:
        return False, "Account not found."

    if new_status not in ("Active", "Frozen", "Closed"):
        return False, "Invalid status."

    acc["status"] = new_status
    add_history(db, "Update Status", acc_id, amount=0)
    return True, f"Status updated to {new_status} ✅"


# ============================================================
# Author: أبو الجبل
#  سحب ايداع حاله حفظ
# ============================================================
def deposit_abo_elgabal(db, acc_id, amount):
    if amount <= 0:
        return False, "Invalid deposit amount."

    acc = db["accounts"].get(acc_id)
    if not acc:
        return False, "Account not found."

    # If Closed, no operations are allowed
    if acc.get("status") == "Closed":
        return False, "Account is Closed and does not accept operations."

    acc["balance"] += float(amount)
    add_history(db, "Deposit", acc_id, amount=float(amount))
    return True, f"Deposited {amount:.2f} EGP ✅"


def withdraw_abo_elgabal(db, acc_id, amount):
    if amount <= 0:
        return False, "Invalid withdrawal amount."

    acc = db["accounts"].get(acc_id)
    if not acc:
        return False, "Account not found."

    # Active فقط للسحب
    if acc.get("status") != "Active":
        return (
            False,
            f"Account is not active ({acc.get('status')}) and does not allow withdrawal.",
        )

    if acc["balance"] < float(amount):
        return False, "Insufficient balance."

    acc["balance"] -= float(amount)
    add_history(db, "Withdraw", acc_id, amount=float(amount))
    return True, f"Withdrawn {amount:.2f} EGP ✅"


# ============================================================
# Author: مصطفى الفيشاوي
# Transaction history helpers (account history / filters)
# ============================================================
def get_account_history_feshawy(db, acc_id):
    return [
        h
        for h in db["history"]
        if h.get("account") == acc_id or h.get("to_account") == acc_id
    ]


# ============================================================
# Author: صبحي
# Dashboard metrics (based on real db not random)
# ============================================================


def get_dashboard_metrics_sobhy(db):
    accounts = db["accounts"]
    history = db["history"]

    total_accounts = len(accounts)
    total_balance = sum(acc.get("balance", 0) for acc in accounts.values())

    today_str = date.today().strftime("%Y-%m-%d")
    today_deposits = sum(
        h["amount"]
        for h in history
        if h["action"] == "Deposit" and h["time"].startswith(today_str)
    )
    today_withdraws = sum(
        h["amount"]
        for h in history
        if h["action"] == "Withdraw" and h["time"].startswith(today_str)
    )
    today_transfers = sum(
        h["amount"]
        for h in history
        if h["action"] == "Transfer" and h["time"].startswith(today_str)
    )

    return {
        "total_accounts": total_accounts,
        "total_balance": total_balance,
        "today_deposits": today_deposits,
        "today_withdraws": today_withdraws,
        "today_transfers": today_transfers,
    }


# ============================================================
# Author: بطه
# Customer data validation + attach to account
# ============================================================
def validate_customer_batta(name: str, phone: str, email: str) -> bool:
    if name == "" or phone == "" or email == "":
        return False
    if not str(phone).isdigit():
        return False
    if "@" not in email:
        return False
    return True


def add_customer_to_account_batta(db, acc_id: str, name: str, phone: str, email: str):
    if acc_id not in db["accounts"]:
        return False, "Account not found."

    if not validate_customer_batta(name, phone, email):
        return False, "Invalid customer data."

    db["accounts"][acc_id]["customer"] = {"name": name, "phone": phone, "email": email}
    add_history(db, "Customer Update", acc_id, amount=0)
    return True, "Customer data saved successfully ✅"


# ============================================================
# Streamlit UI (Main App)
# ============================================================
st.set_page_config(page_title="Bank Management System", layout="wide")

set_background("bg5.png")
st.title("🏦 Bank Management System")

# Session init
if "db" not in st.session_state:
    st.session_state.db = load_database()

if "role" not in st.session_state:
    st.session_state.role = "customer"
    st.session_state.username = "customer"
    st.session_state.logged_in = False

db = st.session_state.db

# Users (Admin/Employee)
USERS = {
    "admin1": {"password": "123", "role": "admin"},
    "employee1": {"password": "123", "role": "employee"},
}

# Sidebar Login
st.sidebar.write(
    f"👤 Current user: {st.session_state.username} ({st.session_state.role})"
)

with st.sidebar.expander("🔐 Staff / Admin Login"):
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login", key="login_btn"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]
            st.session_state.username = username
            st.sidebar.success("Logged in successfully ✅")
        else:
            st.sidebar.error("Invalid login credentials ❌")


if st.session_state.logged_in and st.sidebar.button("Logout", key="logout_btn"):
    st.session_state.logged_in = False
    st.session_state.role = "customer"
    st.session_state.username = "customer"

# =========================================
#       Tabs Menu
# ==========================================
if st.session_state.role in ["admin", "employee"]:
    tab_names = [
        "Dashboard",
        "Open Account",
        "Update Account Status",
        "Deposit",
        "Withdraw",
        "Transfer",
        "Account Details",
        "Customer Data",
        "History",
        "Currency Exchange",
        "Book Appointment",
        "Manage Appointments",
    ]
else:
    tab_names = ["Open Account", "Currency Exchange", "Book Appointment"]


tabs = st.tabs(tab_names)
accounts = db["accounts"]
bank_rafaa = Bank_Rafaa(db)

# ---------------------------
# Dashboard (صبحي)
# ---------------------------
if "Dashboard" in tab_names:
    with tabs[tab_names.index("Dashboard")]:
        st.header("📊 Dashboard")

        metrics = get_dashboard_metrics_sobhy(db)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Accounts", metrics["total_accounts"])
        c2.metric("Total Balance", f"{metrics['total_balance']:.2f} EGP")
        c3.metric("Today's Deposits", f"{metrics['today_deposits']:.2f} EGP")
        c4.metric("Today's Withdrawals", f"{metrics['today_withdraws']:.2f} EGP")
        st.metric("Today's Transfers", f"{metrics['today_transfers']:.2f} EGP")

# ---------------------------
# فتح حساب (مصطفى عيد)
# ---------------------------
with tabs[tab_names.index("Open Account")]:
    st.header("➕ Open Account")

    name = st.text_input("Customer Name:", key="open_name")
    phone = st.text_input("Phone Number:", key="open_phone")
    national_id = st.text_input("National ID (optional):", key="open_nid")
    balance = st.number_input(
        "Initial Balance:", min_value=50.0, value=50.0, key="open_balance"
    )

    if st.button("Create Account", key="open_create_btn"):
        ok, acc_id, msg = create_account_auto_id_eid(
            db, name=name, phone=phone, national_id=national_id, balance=balance
        )
        if ok:
            save_database(db)
            st.success(f"{msg} | Account Number: {acc_id}")
        else:
            st.error(msg)


# ---------------------------
# تحديث حالة حساب (مصطفى عيد)
# ---------------------------
if "Update Account Status" in tab_names:
    with tabs[tab_names.index("Update Account Status")]:
        st.header("🧊 Update Account Status (Active / Frozen / Closed)")

        if st.session_state.role not in ["admin", "employee"]:
            st.error("Access denied")
            st.stop()

        acc_id = st.text_input("Account Number:", key="status_acc")
        new_status = st.selectbox(
            "New Status:", ["Active", "Frozen", "Closed"], key="status_new"
        )

        if st.button("Update Status", key="status_btn"):
            ok, msg = update_status_eid(db, acc_id, new_status)
            if ok:
                save_database(db)
                st.success(msg)
            else:
                st.error(msg)


# ---------------------------
# إيداع (أبو الجبل)
# ---------------------------
if "Deposit" in tab_names:
    with tabs[tab_names.index("Deposit")]:
        st.header("💰 Deposit")

        acc_id = st.text_input("Account Number:", key="dep_acc")
        amount = st.number_input("Amount:", min_value=1.0, value=50.0, key="dep_amt")

        if st.button("Process Deposit", key="dep_btn"):
            ok, msg = deposit_abo_elgabal(db, acc_id, float(amount))
            if ok:
                save_database(db)
                st.success(msg)
            else:
                st.error(msg)


# ---------------------------
# سحب (أبو الجبل)
# ---------------------------
if "Withdraw" in tab_names:
    with tabs[tab_names.index("Withdraw")]:
        st.header("🏧 Withdrawal")

        acc_id = st.text_input("Account Number:", key="wd_acc")
        amount = st.number_input("Amount:", min_value=1.0, value=50.0, key="wd_amt")

        if st.button("Process Withdrawal", key="wd_btn"):
            ok, msg = withdraw_abo_elgabal(db, acc_id, float(amount))
            if ok:
                save_database(db)
                st.success(msg)
            else:
                st.error(msg)


# ---------------------------
# تحويل (محمد رافع)
# ---------------------------
if "Transfer" in tab_names:
    with tabs[tab_names.index("Transfer")]:
        st.header("🔁 Transfer Between Accounts")

        from_acc = st.text_input("Source Account Number:", key="tr_from")
        to_acc = st.text_input("Target Account Number:", key="tr_to")
        amount = st.number_input("Amount:", min_value=1.0, value=100.0, key="tr_amt")

        if st.button("Process Transfer", key="tr_btn"):
            ok, msg = bank_rafaa.transfer(from_acc, to_acc, float(amount))
            if ok:
                save_database(db)
                st.success(msg)
            else:
                st.error(msg)


# ---------------------------
# (تفاصيل: UI عامة + History: مصطفى الفيشاوي)
# ---------------------------
if "Account Details" in tab_names:
    with tabs[tab_names.index("Account Details")]:
        st.header("🔍 Account Details")
        acc_id = st.text_input("Account Number to Search:", key="details_acc")

        if st.button("View Details", key="details_btn"):
            if acc_id not in accounts:
                st.error("Account not found.")
            else:
                acc = accounts[acc_id]
                st.subheader("Account Information")
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.write("### 📌 Basic Information")
                    st.write(f"**Account Number:** {acc_id}")
                    st.write(f"**Customer Name:** {acc.get('name','-')}")
                    st.write(f"**Phone Number:** {acc.get('phone','-')}")
                    st.write(f"**National ID:** {acc.get('national_id','-')}")

                with c2:
                    st.write("### 💰 Balance Information")
                    st.write(f"**Current Balance:** {acc.get('balance',0):.2f} EGP")
                    st.write(f"**Status:** {acc.get('status','-')}")

                with c3:
                    st.write("### 🕒 Timing")
                    st.write(f"**Created At:** {acc.get('created_at','-')}")

                st.markdown("---")

                st.write("### 📜 Account Transaction History")
                hist = get_account_history_feshawy(db, acc_id)
                if hist:
                    st.table(hist)
                else:
                    st.info("No transactions for this account.")

# ---------------------------
# بيانات العميل (بطه)
# ---------------------------
if "Customer Data" in tab_names:
    with tabs[tab_names.index("Customer Data")]:
        st.header("🪪 Add / Update Customer Data on Account")

        acc_id = st.text_input("Account Number:", key="cust_acc")
        cname = st.text_input("Customer Name:", key="cust_name")
        cphone = st.text_input("Customer Phone:", key="cust_phone")
        cemail = st.text_input("Customer Email:", key="cust_email")

        if st.button("Save Customer Data", key="cust_save_btn"):
            ok, msg = add_customer_to_account_batta(db, acc_id, cname, cphone, cemail)
            if ok:
                save_database(db)
                st.success(msg)
            else:
                st.error(msg)

# ---------------------------
# السجل (History)
# ---------------------------
if "History" in tab_names:
    with tabs[tab_names.index("History")]:
        st.header("📜 History")

        col1, col2, col3 = st.columns(3)
        with col1:
            action_filter = st.selectbox(
                "Action Type:",
                [
                    "All",
                    "Create",
                    "Deposit",
                    "Withdraw",
                    "Transfer",
                    "Update Status",
                    "Customer Update",
                ],
                key="hist_action",
            )
        with col2:
            acc_filter = st.text_input(
                "Filter by Account Number (optional):", key="hist_acc"
            )
        with col3:
            today_only = st.checkbox("Show today's transactions only", key="hist_today")

        filtered = db["history"]

        if action_filter != "All":
            filtered = [h for h in filtered if h["action"] == action_filter]

        if acc_filter:
            filtered = [
                h
                for h in filtered
                if acc_filter == h.get("account") or acc_filter == h.get("to_account")
            ]

        if today_only:
            today_str = date.today().strftime("%Y-%m-%d")
            filtered = [h for h in filtered if h["time"].startswith(today_str)]

        if filtered:
            st.table(filtered)
        else:
            st.info("No transactions match the current filters.")


# ---------------------------
# (محمد ايمن)تحويل عملات
# ---------------------------
if "Currency Exchange" in tab_names:
    with tabs[tab_names.index("Currency Exchange")]:
        st.header("💱Currency Exchange")

        currency_list = ["EGP", "USD", "EUR", "GBP", "SAR", "AED", "KWD"]
        currency_rates = {
            "EGP": 1,
            "USD": 47.5,  
            "EUR": 55.8,   
            "GBP": 63.8,   
            "SAR": 12.7,   
            "AED": 13.0,   
            "KWD": 155,   
        }
        
        amount = st.number_input("Amount", min_value=0.0, value=1.0, key="fx_amt")
        from_currency = st.selectbox(
            "From Currency", currency_list, index=1, key="fx_from"
        )
        to_currency = st.selectbox("To Currency", currency_list, index=0, key="fx_to")

        if st.button("Convert", key="fx_btn"):
            amount_in_egp = amount * currency_rates[from_currency]
            final_amount = amount_in_egp / currency_rates[to_currency]

            st.success(
                f"{amount:.2f} {from_currency} = {final_amount:.2f} {to_currency}"
            )
            st.caption("Note: Rates are approximate and fixed (for testing only).")

# ---------------------------
# حجز موعد 🗓️
# ---------------------------
if "Book Appointment" in tab_names:
    with tabs[tab_names.index("Book Appointment")]:
        # ...
        st.header("🗓️ Book an Appointment at the Branch")

        branches = [
            "Nasr City",
            "New Cairo",
            "Heliopolis",
            "Maadi",
            "Dokki",
            "Mohandessin",
            "6th of October",
            "Giza",
            "Alexandria - Smouha",
            "Alexandria - Miami",
            "Mansoura",
            "Tanta",
        ]
        services = [
            "Open Account",
            "Deposit / Withdrawal",
            "Update Data",
            "Inquiry",
            "Complaint",
        ]

        name = st.text_input("Name", key="appt_name")
        phone = st.text_input("Phone Number", key="appt_phone")
        branch = st.selectbox("Branch", branches, key="appt_branch")
        service = st.selectbox("Service Type", services, key="appt_service")
        date_val = st.date_input("Date", key="appt_date")
        time_val = st.selectbox(
            "Time",
            [
                "09:00",
                "09:30",
                "10:00",
                "10:30",
                "11:00",
                "11:30",
                "12:00",
                "12:30",
                "13:00",
                "13:30",
                "14:00",
            ],
            key="appt_time",
        )

        if st.button("Confirm Booking", key="appt_btn"):
            if not name or not phone:
                st.error("Please enter your name and phone number")
            else:
                conflict = False
                for a in db["appointments"]:
                    if (
                        a["branch"] == branch
                        and a["date"] == str(date_val)
                        and a["time"] == time_val
                        and a["status"] in ["Pending", "Approved"]
                    ):
                        conflict = True
                        break

                if conflict:
                    st.error("❌ This time slot is already booked at this branch")
                else:
                    new_id = len(db["appointments"]) + 1
                    db["appointments"].append(
                        {
                            "id": new_id,
                            "name": name,
                            "phone": phone,
                            "branch": branch,
                            "service": service,
                            "date": str(date_val),
                            "time": time_val,
                            "status": "Pending",
                            "note": "",
                        }
                    )
                    save_database(db)
                    st.success(
                        "✅ Appointment booked successfully, awaiting confirmation"
                    )


# ---------------------------
# إدارة المواعيد
# ---------------------------
if "Manage Appointments" in tab_names:
    with tabs[tab_names.index("Manage Appointments")]:
        st.header("🛠️ Branch Appointments Management")

        if not db["appointments"]:
            st.info("No appointments yet")
        else:
            for a in db["appointments"]:
                st.markdown("---")
                st.write(f"🆔 Booking ID: {a['id']}")
                st.write(f"👤 Name: {a['name']}")
                st.write(f"📞 Phone: {a['phone']}")
                st.write(f"🏢 Branch: {a['branch']}")
                st.write(f"🧾 Service: {a['service']}")
                st.write(f"📅 Date: {a['date']} – ⏰ {a['time']}")
                st.write(f"📌 Current Status: {a['status']}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"✅ Approve {a['id']}", key=f"appt_ok_{a['id']}"):
                        a["status"] = "Approved"
                        save_database(db)
                        st.success("Appointment approved")

                with col2:
                    if st.button(f"❌ Reject {a['id']}", key=f"appt_no_{a['id']}"):
                        a["status"] = "Rejected"
                        save_database(db)
                        st.error("Appointment rejected")