"""
MoneyWise CBO Training Portal
Bilingual (Hindi + English) · Mobile Friendly · Professional UI
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

# PDF Topics: Hindi + English
TOPICS = [
    {"hi": "आर्थिक नियोजन (आय-व्यय)", "en": "Financial Planning (Income-Expense)"},
    {"hi": "बचत एवं निवेश", "en": "Savings & Investment"},
    {"hi": "बैंकिंग एवं वित्तीय उत्पाद", "en": "Banking & Financial Products"},
    {"hi": "बीमा", "en": "Insurance"},
    {"hi": "पेंशन (स्वावलंबन)", "en": "Pension (Swaylamban / APY / NPS)"},
    {"hi": "डिजिटल लेनदेन एवं वित्तीय सेवाएँ", "en": "Digital Transactions & Financial Services"},
    {"hi": "लोन / ऋण", "en": "Loan / Credit"},
    {"hi": "व्यवसायिक ऋण", "en": "Business Loan (MSME / Mudra)"},
    {"hi": "बैंकिंग ग्राहक के अधिकार एवं जिम्मेदारियाँ", "en": "Banking Customer Rights & Responsibilities"},
    {"hi": "शिकायत निवारण प्रणाली (लोकपाल)", "en": "Grievance Redressal (Ombudsman)"},
    {"hi": "बुनियादी वित्तीय साक्षरता", "en": "Basic Financial Literacy"},
    {"hi": "बुनियादी गणितीय कौशल", "en": "Basic Mathematical Skills"},
    {"hi": "CRISIL Foundation / SOP", "en": "CRISIL Foundation / Project SOP"},
    {"hi": "KYC / Re-KYC", "en": "KYC / Re-KYC"},
    {"hi": "सोशल सिक्योरिटी स्कीम (PMJDY, PMSBY, PMJJBY)", "en": "Social Security Schemes (PMJDY, PMSBY, PMJJBY)"},
    {"hi": "फ्रॉड प्रिवेंशन / साइबर फ्रॉड", "en": "Fraud Prevention / Cyber Fraud"},
    {"hi": "NABARD / RBI / PACS", "en": "NABARD / RBI / PACS"},
    {"hi": "अन्य", "en": "Other"},
]

PHASES = [
    {"hi": "Phase-II", "en": "Phase-II"},
    {"hi": "Phase-III", "en": "Phase-III"},
    {"hi": "Extension Phase - 1", "en": "Extension Phase - 1"},
]

TRAINING_TYPES = [
    {"hi": "फिजिकल (Physical)", "en": "Physical"},
    {"hi": "वर्चुअल (Virtual)", "en": "Virtual"},
]

# -------------------- i18n --------------------
T = {
    "en": {
        "app_title": "MoneyWise",
        "app_sub": "CBO Training & Capacity Building Portal",
        "login": "CBO Login",
        "select_name": "Select your name",
        "password": "Password",
        "sign_in": "Sign In",
        "demo_pwd": "Demo password: cbo123",
        "wrong_pwd": "Incorrect password",
        "menu_dashboard": "Dashboard",
        "menu_team": "My Team",
        "menu_entry": "Data Entry",
        "menu_report": "Report",
        "logout": "Logout",
        "welcome": "Welcome",
        "district": "District",
        "block": "Block",
        "total_team": "Total Team",
        "fc": "Field Coordinators",
        "cm": "Centre Managers",
        "deo": "Data Entry Operators",
        "trainings_done": "Trainings Done",
        "recent": "Recent Entries",
        "no_entries": "No entries yet. Use Data Entry to add.",
        "my_team": "My Team",
        "members_under": "members under",
        "filter_desig": "Filter Designation",
        "search": "Search name / ID / mobile",
        "download": "Download CSV",
        "data_entry": "Data Entry Form",
        "data_entry_sub": "Physical / Virtual Training · Staff Attendance",
        "basic": "Basic Details",
        "date": "Date",
        "training_type": "Training Type",
        "activity_date": "Activity Date",
        "topic": "Training Topic",
        "phase": "Phase",
        "numbers": "Numbers",
        "no_physical": "No. of Physical",
        "no_virtual": "No. of Virtual",
        "staff_list": "Staff List (tick present)",
        "staff_hint": "Your mapped FC / CM / DEO",
        "remarks": "Remarks (optional)",
        "save": "Save Entry",
        "saved": "Saved successfully",
        "staff_present": "staff marked present",
        "report": "Report",
        "report_sub": "Summary · Phase-wise · Topic-wise",
        "total_entries": "Total Entries",
        "physical": "Physical",
        "virtual": "Virtual",
        "unique_topics": "Unique Topics",
        "phase_summary": "Phase-wise Summary",
        "topic_summary": "Topic-wise Coverage",
        "all_entries": "All Entries",
        "download_report": "Download Full Report",
        "no_data": "No data. Please add from Data Entry.",
        "lang": "Language",
    },
    "hi": {
        "app_title": "MoneyWise",
        "app_sub": "सीबीओ प्रशिक्षण एवं क्षमता निर्माण पोर्टल",
        "login": "सीबीओ लॉगिन",
        "select_name": "अपना नाम चुनें",
        "password": "पासवर्ड",
        "sign_in": "साइन इन",
        "demo_pwd": "डेमो पासवर्ड: cbo123",
        "wrong_pwd": "गलत पासवर्ड",
        "menu_dashboard": "डैशबोर्ड",
        "menu_team": "मेरी टीम",
        "menu_entry": "डेटा एंट्री",
        "menu_report": "रिपोर्ट",
        "logout": "लॉगआउट",
        "welcome": "नमस्ते",
        "district": "जिला",
        "block": "ब्लॉक",
        "total_team": "कुल टीम",
        "fc": "फील्ड कोऑर्डिनेटर",
        "cm": "सेंटर मैनेजर",
        "deo": "डेटा एंट्री ऑपरेटर",
        "trainings_done": "प्रशिक्षण पूर्ण",
        "recent": "हाल की एंट्री",
        "no_entries": "अभी कोई एंट्री नहीं। डेटा एंट्री से जोड़ें।",
        "my_team": "मेरी टीम",
        "members_under": "सदस्य",
        "filter_desig": "पद फ़िल्टर",
        "search": "नाम / ID / मोबाइल खोजें",
        "download": "CSV डाउनलोड",
        "data_entry": "डेटा एंट्री फॉर्म",
        "data_entry_sub": "फिजिकल / वर्चुअल प्रशिक्षण · स्टाफ उपस्थिति",
        "basic": "मूल जानकारी",
        "date": "दिनांक",
        "training_type": "प्रशिक्षण प्रकार",
        "activity_date": "गतिविधि तिथि",
        "topic": "प्रशिक्षण विषय",
        "phase": "चरण",
        "numbers": "संख्या",
        "no_physical": "फिजिकल संख्या",
        "no_virtual": "वर्चुअल संख्या",
        "staff_list": "स्टाफ सूची (टिक करें)",
        "staff_hint": "आपके मैप किए गए FC / CM / DEO",
        "remarks": "टिप्पणी (वैकल्पिक)",
        "save": "सेव करें",
        "saved": "सफलतापूर्वक सेव हो गया",
        "staff_present": "स्टाफ उपस्थित",
        "report": "रिपोर्ट",
        "report_sub": "सारांश · चरणवार · विषयवार",
        "total_entries": "कुल एंट्री",
        "physical": "फिजिकल",
        "virtual": "वर्चुअल",
        "unique_topics": "विषयों की संख्या",
        "phase_summary": "चरणवार सारांश",
        "topic_summary": "विषयवार कवरेज",
        "all_entries": "सभी एंट्री",
        "download_report": "पूरी रिपोर्ट डाउनलोड",
        "no_data": "कोई डेटा नहीं। डेटा एंट्री से जोड़ें।",
        "lang": "भाषा",
    },
}

def t(key):
    lang = st.session_state.get("lang", "en")
    return T.get(lang, T["en"]).get(key, key)

def topic_label(item):
    lang = st.session_state.get("lang", "en")
    return item.get(lang, item["en"])

# -------------------- DB --------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS training_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cbo_id TEXT,
            cbo_name TEXT,
            district TEXT,
            block TEXT,
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

# -------------------- CSS (Professional + Mobile) --------------------
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }

    /* Header */
    .app-header {
        background: linear-gradient(135deg, #0b3d5c 0%, #1a6b9a 60%, #2a9d8f 100%);
        color: #fff;
        padding: 1rem 1.25rem;
        border-radius: 14px;
        margin-bottom: 1.25rem;
        box-shadow: 0 6px 20px rgba(11,61,92,0.28);
    }
    .app-header h1 { margin: 0; font-size: 1.35rem; font-weight: 700; color: #fff !important; }
    .app-header p { margin: 0.25rem 0 0; font-size: 0.85rem; opacity: 0.92; color: #fff !important; }

    /* Metric cards */
    .m-card {
        background: #fff;
        border: 1px solid #e8ecf0;
        border-radius: 12px;
        padding: 0.9rem 0.75rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.15s;
    }
    .m-card:hover { transform: translateY(-2px); }
    .m-val { font-size: 1.55rem; font-weight: 700; color: #0b3d5c; line-height: 1.2; }
    .m-lbl { font-size: 0.72rem; color: #64748b; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.03em; }

    .sec {
        font-size: 1rem; font-weight: 600; color: #0f172a;
        margin: 1.1rem 0 0.6rem; padding-bottom: 0.35rem;
        border-bottom: 2.5px solid #1a6b9a;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f0f7fb 0%, #e8f0f5 100%);
        border-right: 1px solid #d0e0ea;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-weight: 500; padding: 0.35rem 0;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0b3d5c, #1a6b9a);
        color: white; border: none; border-radius: 10px;
        font-weight: 600; padding: 0.55rem 1.4rem;
        box-shadow: 0 3px 10px rgba(11,61,92,0.25);
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #08304a, #155a82);
    }

    /* Login */
    .login-wrap { max-width: 400px; margin: 2.5rem auto; }

    /* Mobile */
    @media (max-width: 768px) {
        .app-header h1 { font-size: 1.15rem; }
        .m-val { font-size: 1.3rem; }
        .m-lbl { font-size: 0.65rem; }
        div[data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
    }

    /* Form polish */
    .stTextInput input, .stSelectbox, .stNumberInput input, .stDateInput input {
        border-radius: 8px !important;
    }
    div[data-testid="stForm"] {
        background: #fafbfc; padding: 1.25rem; border-radius: 14px;
        border: 1px solid #e8ecf0;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------- LOGIN --------------------
def login_page():
    inject_css()
    st.markdown(f"""
    <div style="text-align:center;padding:1.5rem 0 0.5rem;">
        <h1 style="color:#0b3d5c;font-weight:700;margin:0;">{t("app_title")}</h1>
        <p style="color:#64748b;margin:0.3rem 0 0;">{t("app_sub")}</p>
    </div>
    """, unsafe_allow_html=True)

    # Language toggle
    lang_col1, lang_col2, lang_col3 = st.columns([2, 1, 2])
    with lang_col2:
        lang = st.radio("", ["English", "हिन्दी"], horizontal=True, label_visibility="collapsed",
                        index=0 if st.session_state.get("lang", "en") == "en" else 1)
        st.session_state.lang = "en" if lang == "English" else "hi"

    leaders = load_leaders()
    options = {
        f"{r['Consultant']} ({r['Consultant No']}) · {r['Working Location']}": r["Consultant No"]
        for _, r in leaders.iterrows()
    }

    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown(f"##### {t('login')}")
    selected = st.selectbox(t("select_name"), list(options.keys()), label_visibility="collapsed")
    pwd = st.text_input(t("password"), type="password", value="cbo123")
    if st.button(t("sign_in"), type="primary", use_container_width=True):
        if pwd.strip() == "cbo123":
            cid = options[selected]
            row = leaders[leaders["Consultant No"] == cid].iloc[0]
            st.session_state.logged_in = True
            st.session_state.cbo_id = cid
            st.session_state.cbo_name = row["Consultant"]
            st.session_state.cbo_district = row["Working Location"]
            st.session_state.cbo_desig = row["Designation"]
            st.rerun()
        else:
            st.error(t("wrong_pwd"))
    st.caption(t("demo_pwd"))
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- DASHBOARD --------------------
def page_dashboard(staff_df):
    cbo_id = st.session_state.cbo_id
    team = get_team(cbo_id, staff_df)
    district = st.session_state.get("cbo_district", "—")

    st.markdown(f"""
    <div class="app-header">
        <h1>{t("welcome")}, {st.session_state.cbo_name}</h1>
        <p>{st.session_state.cbo_desig} &nbsp;|&nbsp; {t("district")}: {district} &nbsp;|&nbsp; ID: {cbo_id}</p>
    </div>
    """, unsafe_allow_html=True)

    fc = len(team[team["Designation"].str.contains("Field Coordinator", na=False)])
    cm = len(team[team["Designation"].str.contains("Centre Manager", na=False)])
    deo = len(team[team["Designation"].str.contains("Data Entry Operator", na=False)])

    conn = get_conn()
    stats = pd.read_sql_query(
        "SELECT COUNT(*) as total FROM training_entries WHERE cbo_id=?", conn, params=(cbo_id,)
    )
    recent = pd.read_sql_query(
        "SELECT entry_date, training_type, topic, activity_date, phase, no_physical, no_virtual FROM training_entries WHERE cbo_id=? ORDER BY id DESC LIMIT 8",
        conn, params=(cbo_id,)
    )
    conn.close()

    cols = st.columns(5)
    metrics = [
        (len(team), t("total_team")),
        (fc, t("fc")),
        (cm, t("cm")),
        (deo, t("deo")),
        (int(stats["total"].iloc[0] or 0), t("trainings_done")),
    ]
    for col, (val, lbl) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="m-card"><div class="m-val">{val}</div><div class="m-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="sec">{t("recent")}</div>', unsafe_allow_html=True)
    if recent.empty:
        st.info(t("no_entries"))
    else:
        st.dataframe(recent, use_container_width=True, hide_index=True)

# -------------------- TEAM --------------------
def page_team(staff_df):
    cbo_id = st.session_state.cbo_id
    team = get_team(cbo_id, staff_df)
    district = st.session_state.get("cbo_district", "—")

    st.markdown(f"""
    <div class="app-header">
        <h1>{t("my_team")}</h1>
        <p>{len(team)} {t("members_under")} {st.session_state.cbo_name} · {t("district")}: {district}</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        desigs = st.multiselect(t("filter_desig"), sorted(team["Designation"].unique()),
                                default=list(team["Designation"].unique()))
    with c2:
        search = st.text_input(t("search"), placeholder="...")

    filtered = team[team["Designation"].isin(desigs)] if desigs else team
    if search:
        m = (
            filtered["Consultant"].str.contains(search, case=False, na=False) |
            filtered["Consultant No"].str.contains(search, case=False, na=False) |
            filtered["Mobile No"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[m]

    show = filtered[["Consultant No", "Consultant", "Designation", "Working Location", "Mobile No", "Gender", "Aging"]].copy()
    show["Designation"] = show["Designation"].str.replace("Consultant (", "").str.replace(")", "")
    st.dataframe(show, use_container_width=True, hide_index=True, height=400)
    st.download_button(t("download"), show.to_csv(index=False).encode("utf-8-sig"),
                       f"team_{cbo_id}.csv", "text/csv")

# -------------------- DATA ENTRY (no validation) --------------------
def page_entry(staff_df):
    cbo_id = st.session_state.cbo_id
    cbo_name = st.session_state.cbo_name
    district = st.session_state.get("cbo_district", "")
    team = get_team(cbo_id, staff_df)

    st.markdown(f"""
    <div class="app-header">
        <h1>{t("data_entry")}</h1>
        <p>{t("data_entry_sub")} · {t("district")}: {district}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("entry_form", clear_on_submit=True):
        st.markdown(f"**{t('basic')}**")
        r1 = st.columns(3)
        with r1[0]:
            entry_date = st.date_input(t("date"), value=date.today())
        with r1[1]:
            type_opts = [topic_label(x) for x in TRAINING_TYPES]
            training_type = st.selectbox(t("training_type"), type_opts)
        with r1[2]:
            activity_date = st.date_input(t("activity_date"), value=date.today())

        r2 = st.columns(2)
        with r2[0]:
            topic_opts = [topic_label(x) for x in TOPICS]
            topic = st.selectbox(t("topic"), topic_opts)
        with r2[1]:
            phase_opts = [topic_label(x) for x in PHASES]
            phase = st.selectbox(t("phase"), phase_opts)

        r3 = st.columns(2)
        with r3[0]:
            block = st.text_input(t("block"), placeholder="Block name (optional)")
        with r3[1]:
            st.text_input(t("district"), value=district, disabled=True)

        st.markdown(f"**{t('numbers')}**")
        n1, n2 = st.columns(2)
        with n1:
            no_physical = st.number_input(t("no_physical"), min_value=0, value=0)
        with n2:
            no_virtual = st.number_input(t("no_virtual"), min_value=0, value=0)

        st.markdown(f"**{t('staff_list')}**")
        st.caption(t("staff_hint"))

        present_ids, present_names = [], []
        for label, kw in [("FC", "Field Coordinator"), ("CM", "Centre Manager"), ("DEO", "Data Entry Operator")]:
            sub = team[team["Designation"].str.contains(kw, na=False)]
            if not sub.empty:
                st.markdown(f"**{label}** ({len(sub)})")
                cols = st.columns(2 if st.session_state.get("lang") == "hi" else 3)
                for i, (_, row) in enumerate(sub.iterrows()):
                    with cols[i % len(cols)]:
                        short = f"{row['Consultant']} ({str(row['Consultant No'])[-5:]})"
                        if st.checkbox(short, key=f"s_{row['Consultant No']}"):
                            present_ids.append(row["Consultant No"])
                            present_names.append(row["Consultant"])

        other = team[~team["Designation"].str.contains("Field Coordinator|Centre Manager|Data Entry Operator", na=False)]
        if not other.empty:
            st.markdown("**Other**")
            for _, row in other.iterrows():
                if st.checkbox(f"{row['Consultant']}", key=f"s_{row['Consultant No']}"):
                    present_ids.append(row["Consultant No"])
                    present_names.append(row["Consultant"])

        remarks = st.text_area(t("remarks"), height=70)

        # NO VALIDATION — always allow save
        if st.form_submit_button(t("save"), type="primary", use_container_width=True):
            conn = get_conn()
            c = conn.cursor()
            c.execute("""
                INSERT INTO training_entries
                (cbo_id, cbo_name, district, block, entry_date, training_type, topic, activity_date, phase,
                 no_physical, no_virtual, staff_ids, staff_names, remarks, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                cbo_id, cbo_name, district, block or "", str(entry_date), training_type, topic,
                str(activity_date), phase, no_physical, no_virtual,
                ",".join(present_ids), ",".join(present_names), remarks or "",
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
            st.success(f"{t('saved')} · {len(present_ids)} {t('staff_present')}")
            st.balloons()

# -------------------- REPORT --------------------
def page_report():
    cbo_id = st.session_state.cbo_id
    district = st.session_state.get("cbo_district", "—")

    st.markdown(f"""
    <div class="app-header">
        <h1>{t("report")}</h1>
        <p>{t("report_sub")} · {t("district")}: {district}</p>
    </div>
    """, unsafe_allow_html=True)

    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM training_entries WHERE cbo_id=? ORDER BY activity_date DESC, id DESC",
        conn, params=(cbo_id,)
    )
    conn.close()

    if df.empty:
        st.info(t("no_data"))
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(t("total_entries"), len(df))
    k2.metric(t("physical"), int(df["no_physical"].sum()))
    k3.metric(t("virtual"), int(df["no_virtual"].sum()))
    k4.metric(t("unique_topics"), df["topic"].nunique())

    st.markdown(f'<div class="sec">{t("phase_summary")}</div>', unsafe_allow_html=True)
    ph = df.groupby("phase").agg(Entries=("id", "count"), Physical=("no_physical", "sum"), Virtual=("no_virtual", "sum")).reset_index()
    st.dataframe(ph, use_container_width=True, hide_index=True)

    st.markdown(f'<div class="sec">{t("topic_summary")}</div>', unsafe_allow_html=True)
    tp = df.groupby("topic").agg(Count=("id", "count"), Physical=("no_physical", "sum"), Virtual=("no_virtual", "sum")).reset_index().sort_values("Count", ascending=False)
    st.dataframe(tp, use_container_width=True, hide_index=True)

    st.markdown(f'<div class="sec">{t("all_entries")}</div>', unsafe_allow_html=True)
    show = df[["entry_date", "activity_date", "training_type", "topic", "phase", "district", "block",
               "no_physical", "no_virtual", "staff_names"]].copy()
    st.dataframe(show, use_container_width=True, hide_index=True)

    st.download_button(t("download_report"), df.to_csv(index=False).encode("utf-8-sig"),
                       f"report_{cbo_id}_{date.today()}.csv", "text/csv")

# -------------------- MAIN --------------------
def main():
    st.set_page_config(
        page_title="MoneyWise CBO Portal",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="auto",
    )
    init_db()
    if "lang" not in st.session_state:
        st.session_state.lang = "en"

    inject_css()
    staff_df = load_staff()

    if not st.session_state.get("logged_in"):
        login_page()
        return

    with st.sidebar:
        st.markdown(f"**{st.session_state.cbo_name}**")
        st.caption(f"{st.session_state.cbo_id}")
        st.caption(f"{t('district')}: {st.session_state.get('cbo_district', '—')}")
        st.divider()

        # Language in sidebar
        lang_sel = st.radio(t("lang"), ["English", "हिन्दी"],
                            index=0 if st.session_state.lang == "en" else 1, horizontal=True)
        st.session_state.lang = "en" if lang_sel == "English" else "hi"

        st.divider()
        page = st.radio(
            "Menu",
            [t("menu_dashboard"), t("menu_team"), t("menu_entry"), t("menu_report")],
            label_visibility="collapsed",
        )
        st.divider()
        if st.button(t("logout"), use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # Map page by current language labels
    if page in (T["en"]["menu_dashboard"], T["hi"]["menu_dashboard"]):
        page_dashboard(staff_df)
    elif page in (T["en"]["menu_team"], T["hi"]["menu_team"]):
        page_team(staff_df)
    elif page in (T["en"]["menu_entry"], T["hi"]["menu_entry"]):
        page_entry(staff_df)
    else:
        page_report()

if __name__ == "__main__":
    main()
