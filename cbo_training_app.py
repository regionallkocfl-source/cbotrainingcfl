"""
MoneyWise CBO Training Portal
Professional Data Entry Form + Report
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import os

# -------------------- CONFIG --------------------
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
STAFF_CSV = os.path.join(DATA_DIR, "active_staff.csv")
DB_PATH = os.path.join("/tmp", "cbo_training.db") if os.path.exists("/tmp") else os.path.join(DATA_DIR, "cbo_training.db")

TOPICS = [
    "CRISIL Foundation / SOP of Project",
    "KYC / Re-KYC",
    "Digital Banking & Digital Lending",
    "Social Security Schemes (PMJDY, PMSBY, PMJJBY, APY, NPS)",
    "Banking Ombudsman / One Nation One Ombudsman",
    "Mutual Funds / SIP",
    "Savings, RD, FD, ATM",
    "MSME / Mudra Loan / CM YUVA",
    "Insurance & Financial Planning",
    "Fraud Prevention / Cyber Fraud",
    "NABARD / RBI / PACS",
    "Communication Skills for Effective Session",
    "Input Reporting Form Filling",
    "Other"
]

PHASES = ["Phase-II", "Phase-III", "Extension Phase - 1"]

# -------------------- DB --------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS training_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cbo_id TEXT NOT NULL,
            cbo_name TEXT,
            entry_date TEXT,
            training_type TEXT,
            topic TEXT,
            activity_date TEXT,
            phase TEXT,
            no_physical INTEGER DEFAULT 0,
            no_virtual INTEGER DEFAULT 0,
            staff_ids TEXT,
            staff_names TEXT,
            remarks TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_PATH)

# -------------------- DATA --------------------
@st.cache_data
def load_staff():
    df = pd.read_csv(STAFF_CSV)
    df["Mobile No"] = df["Mobile No"].astype(str)
    return df

@st.cache_data
def load_leaders():
    df = load_staff()
    ids = df["Primary_ID"].dropna().unique().tolist()
    leaders = df[df["Consultant No"].isin(ids)][
        ["Consultant No", "Consultant", "Designation", "Working Location", "Mobile No"]
    ].drop_duplicates().sort_values("Consultant").reset_index(drop=True)
    return leaders

def get_team(cbo_id, staff_df):
    return staff_df[staff_df["Primary_ID"] == cbo_id].copy()

# -------------------- STYLES --------------------
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0f4c81 0%, #1a73a8 100%);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(15,76,129,0.25);
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
        color: white !important;
    }
    .main-header p {
        margin: 0.3rem 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
        color: white !important;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f4c81;
    }
    .metric-card .label {
        font-size: 0.8rem;
        color: #6b7280;
        margin-top: 0.2rem;
    }

    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #111827;
        margin: 1.2rem 0 0.8rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #0f4c81;
    }

    div[data-testid="stSidebar"] {
        background: #f8fafc;
    }

    .stButton > button[kind="primary"] {
        background: #0f4c81;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button[kind="primary"]:hover {
        background: #0a3a63;
    }

    .login-box {
        max-width: 420px;
        margin: 3rem auto;
        padding: 2rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------- LOGIN --------------------
def login_page():
    inject_css()
    st.markdown("""
    <div style="text-align:center; margin-top:2rem;">
        <h1 style="color:#0f4c81; font-weight:700;">MoneyWise</h1>
        <p style="color:#6b7280;">CBO Training & Capacity Building Portal</p>
    </div>
    """, unsafe_allow_html=True)

    leaders = load_leaders()
    options = {
        f"{r['Consultant']}  ({r['Consultant No']})  ·  {r['Working Location']}": r["Consultant No"]
        for _, r in leaders.iterrows()
    }

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("#### CBO Login")
        selected = st.selectbox("Select your name", list(options.keys()), label_visibility="collapsed")
        pwd = st.text_input("Password", type="password", value="cbo123", placeholder="Enter password")
        if st.button("Sign In", type="primary", use_container_width=True):
            if pwd == "cbo123":
                cid = options[selected]
                row = leaders[leaders["Consultant No"] == cid].iloc[0]
                st.session_state.logged_in = True
                st.session_state.cbo_id = cid
                st.session_state.cbo_name = row["Consultant"]
                st.session_state.cbo_loc = row["Working Location"]
                st.session_state.cbo_desig = row["Designation"]
                st.rerun()
            else:
                st.error("Incorrect password. Use: cbo123")
        st.caption("Demo password: **cbo123**")

# -------------------- DASHBOARD --------------------
def page_dashboard(staff_df):
    cbo_id = st.session_state.cbo_id
    team = get_team(cbo_id, staff_df)

    st.markdown(f"""
    <div class="main-header">
        <h1>Welcome, {st.session_state.cbo_name}</h1>
        <p>{st.session_state.cbo_desig} &nbsp;|&nbsp; {st.session_state.cbo_loc} &nbsp;|&nbsp; ID: {cbo_id}</p>
    </div>
    """, unsafe_allow_html=True)

    fc = len(team[team["Designation"].str.contains("Field Coordinator", na=False)])
    cm = len(team[team["Designation"].str.contains("Centre Manager", na=False)])
    deo = len(team[team["Designation"].str.contains("Data Entry Operator", na=False)])

    conn = get_conn()
    stats = pd.read_sql_query(
        "SELECT COUNT(*) as total, COALESCE(SUM(no_physical),0) as phys, COALESCE(SUM(no_virtual),0) as virt FROM training_entries WHERE cbo_id=?",
        conn, params=(cbo_id,)
    )
    recent = pd.read_sql_query(
        "SELECT entry_date, training_type, topic, activity_date, phase, no_physical, no_virtual FROM training_entries WHERE cbo_id=? ORDER BY id DESC LIMIT 8",
        conn, params=(cbo_id,)
    )
    conn.close()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="value">{len(team)}</div><div class="label">Total Team</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="value">{fc}</div><div class="label">Field Coordinators</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="value">{cm}</div><div class="label">Centre Managers</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="value">{deo}</div><div class="label">Data Entry Operators</div></div>', unsafe_allow_html=True)
    with c5:
        total_entries = int(stats["total"].iloc[0] or 0)
        st.markdown(f'<div class="metric-card"><div class="value">{total_entries}</div><div class="label">Trainings Done</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Recent Training Entries</div>', unsafe_allow_html=True)
    if recent.empty:
        st.info("No training entries yet. Go to **Data Entry Form** to add one.")
    else:
        st.dataframe(recent, use_container_width=True, hide_index=True)

# -------------------- TEAM LIST --------------------
def page_team(staff_df):
    cbo_id = st.session_state.cbo_id
    team = get_team(cbo_id, staff_df)

    st.markdown(f"""
    <div class="main-header">
        <h1>My Team</h1>
        <p>{len(team)} members under {st.session_state.cbo_name}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 2])
    with col1:
        desigs = st.multiselect("Filter Designation", sorted(team["Designation"].unique()), default=list(team["Designation"].unique()))
    with col2:
        search = st.text_input("Search name / ID / mobile")

    filtered = team[team["Designation"].isin(desigs)]
    if search:
        m = (
            filtered["Consultant"].str.contains(search, case=False, na=False) |
            filtered["Consultant No"].str.contains(search, case=False, na=False) |
            filtered["Mobile No"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[m]

    show = filtered[["Consultant No", "Consultant", "Designation", "Working Location", "Mobile No", "Gender", "Aging", "BCC Code"]].copy()
    show["Designation"] = show["Designation"].str.replace("Consultant (", "").str.replace(")", "")
    st.dataframe(show, use_container_width=True, hide_index=True, height=420)

    st.download_button("Download CSV", show.to_csv(index=False).encode("utf-8-sig"),
                       f"team_{cbo_id}_{date.today()}.csv", "text/csv")

# -------------------- DATA ENTRY FORM --------------------
def page_entry(staff_df):
    cbo_id = st.session_state.cbo_id
    cbo_name = st.session_state.cbo_name
    team = get_team(cbo_id, staff_df)

    st.markdown(f"""
    <div class="main-header">
        <h1>Data Entry Form</h1>
        <p>Record Physical / Virtual Training · CBO-wise Staff Attendance</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("entry_form", clear_on_submit=True):
        st.markdown("**Basic Details**")
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            entry_date = st.date_input("Date", value=date.today())
        with r1c2:
            training_type = st.selectbox("Training Type", ["Physical", "Virtual"])
        with r1c3:
            activity_date = st.date_input("Activity Date", value=date.today())

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            topic = st.selectbox("Training Topic", TOPICS)
        with r2c2:
            phase = st.selectbox("Phase", PHASES)

        st.markdown("**Numbers**")
        n1, n2 = st.columns(2)
        with n1:
            no_physical = st.number_input("No. of Physical Training", min_value=0, value=1 if training_type == "Physical" else 0)
        with n2:
            no_virtual = st.number_input("No. of Virtual Training", min_value=0, value=1 if training_type == "Virtual" else 0)

        st.markdown("**Staff List (Tick present staff)**")
        st.caption("Only your mapped FC / CM / DEO are shown")

        present_ids = []
        present_names = []

        for desig_label, keyword in [
            ("Field Coordinators", "Field Coordinator"),
            ("Centre Managers", "Centre Manager"),
            ("Data Entry Operators", "Data Entry Operator"),
        ]:
            subset = team[team["Designation"].str.contains(keyword, na=False)]
            if not subset.empty:
                st.markdown(f"**{desig_label}** ({len(subset)})")
                cols = st.columns(3)
                for idx, (_, row) in enumerate(subset.iterrows()):
                    with cols[idx % 3]:
                        label = f"{row['Consultant']} ({row['Consultant No'][-5:]})"
                        if st.checkbox(label, key=f"staff_{row['Consultant No']}"):
                            present_ids.append(row["Consultant No"])
                            present_names.append(row["Consultant"])

        other = team[~team["Designation"].str.contains("Field Coordinator|Centre Manager|Data Entry Operator", na=False)]
        if not other.empty:
            st.markdown("**Other**")
            for _, row in other.iterrows():
                if st.checkbox(f"{row['Consultant']} ({row['Designation']})", key=f"staff_{row['Consultant No']}"):
                    present_ids.append(row["Consultant No"])
                    present_names.append(row["Consultant"])

        remarks = st.text_area("Remarks (optional)", height=80)

        submitted = st.form_submit_button("Save Entry", type="primary", use_container_width=True)

        if submitted:
            if not present_ids:
                st.warning("Please tick at least one staff member.")
            else:
                conn = get_conn()
                c = conn.cursor()
                c.execute("""
                    INSERT INTO training_entries
                    (cbo_id, cbo_name, entry_date, training_type, topic, activity_date, phase,
                     no_physical, no_virtual, staff_ids, staff_names, remarks, created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    cbo_id, cbo_name, str(entry_date), training_type, topic, str(activity_date), phase,
                    no_physical, no_virtual, ",".join(present_ids), ",".join(present_names),
                    remarks, datetime.now().isoformat()
                ))
                conn.commit()
                conn.close()
                st.success(f"Saved successfully · {len(present_ids)} staff marked present")
                st.balloons()

# -------------------- REPORT --------------------
def page_report():
    cbo_id = st.session_state.cbo_id

    st.markdown(f"""
    <div class="main-header">
        <h1>Report</h1>
        <p>Training Summary · Phase-wise · Topic-wise</p>
    </div>
    """, unsafe_allow_html=True)

    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM training_entries WHERE cbo_id=? ORDER BY activity_date DESC, id DESC",
        conn, params=(cbo_id,)
    )
    conn.close()

    if df.empty:
        st.info("No entries found. Please add data from the Data Entry Form.")
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Entries", len(df))
    k2.metric("Physical Trainings", int(df["no_physical"].sum()))
    k3.metric("Virtual Trainings", int(df["no_virtual"].sum()))
    k4.metric("Unique Topics", df["topic"].nunique())

    st.markdown('<div class="section-title">Phase-wise Summary</div>', unsafe_allow_html=True)
    phase_summary = df.groupby("phase").agg(
        Entries=("id", "count"),
        Physical=("no_physical", "sum"),
        Virtual=("no_virtual", "sum")
    ).reset_index()
    st.dataframe(phase_summary, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">Topic-wise Coverage</div>', unsafe_allow_html=True)
    topic_summary = df.groupby("topic").agg(
        Count=("id", "count"),
        Physical=("no_physical", "sum"),
        Virtual=("no_virtual", "sum")
    ).reset_index().sort_values("Count", ascending=False)
    st.dataframe(topic_summary, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">All Entries</div>', unsafe_allow_html=True)
    display = df[[
        "entry_date", "activity_date", "training_type", "topic", "phase",
        "no_physical", "no_virtual", "staff_names"
    ]].rename(columns={
        "entry_date": "Date",
        "activity_date": "Activity Date",
        "training_type": "Type",
        "topic": "Topic",
        "phase": "Phase",
        "no_physical": "Physical",
        "no_virtual": "Virtual",
        "staff_names": "Staff Present"
    })
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.download_button(
        "Download Full Report (CSV)",
        df.to_csv(index=False).encode("utf-8-sig"),
        f"training_report_{cbo_id}_{date.today()}.csv",
        "text/csv"
    )

# -------------------- MAIN --------------------
def main():
    st.set_page_config(
        page_title="MoneyWise CBO Portal",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    init_db()
    inject_css()
    staff_df = load_staff()

    if not st.session_state.get("logged_in"):
        login_page()
        return

    with st.sidebar:
        st.markdown(f"**{st.session_state.cbo_name}**")
        st.caption(f"{st.session_state.cbo_id} · {st.session_state.cbo_loc}")
        st.divider()
        page = st.radio(
            "Menu",
            ["Dashboard", "My Team", "Data Entry Form", "Report"],
            label_visibility="collapsed"
        )
        st.divider()
        if st.button("Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    if page == "Dashboard":
        page_dashboard(staff_df)
    elif page == "My Team":
        page_team(staff_df)
    elif page == "Data Entry Form":
        page_entry(staff_df)
    elif page == "Report":
        page_report()

if __name__ == "__main__":
    main()
