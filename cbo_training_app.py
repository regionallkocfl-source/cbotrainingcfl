"""
CBO Training & Camp Reporting Web App
MoneyWise / CRISIL Foundation - Financial Literacy Project
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import os

# -------------------- CONFIG --------------------
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
STAFF_CSV = os.path.join(DATA_DIR, "active_staff.csv")
# Use /tmp on cloud so SQLite is always writable
DB_PATH = os.path.join("/tmp", "training_app.db") if os.path.exists("/tmp") else os.path.join(DATA_DIR, "training_app.db")

# Topics from the official Input Reporting Format PDF
CAMP_TOPICS = [
    "आर्थिक नियोजन (आय-व्यय)",
    "बचत एवं निवेश",
    "बैंकिंग एवं वित्तीय उत्पाद",
    "बीमा",
    "पेंशन (स्वावलंबन)",
    "डिजिटल लेनदेन एवं वित्तीय सेवाएँ",
    "लोन / ऋण",
    "व्यवसायिक ऋण",
    "बैंकिंग ग्राहक के अधिकार एवं जिम्मेदारियाँ",
    "शिकायत निवारण प्रणाली (लोकपाल)",
    "बुनियादी वित्तीय साक्षरता",
    "बुनियादी गणितीय कौशल",
    "अन्य"
]

GROUP_TYPES = [
    "स्वयं सहायता समूह (SHG)",
    "म्युचुअल सपोर्ट समूह",
    "मिश्रित वर्ग",
    "किसान वर्ग",
    "अन्य"
]

TRAINING_METHODS = [
    "ऑडियो विजुअल (AVT)",
    "फिल्म/वीडियो (FBT)",
    "खेल",
    "व्याख्यान",
    "अन्य"
]

CAMP_TYPES = ["प्रशिक्षण (Training)", "जागरूकता (Awareness)", "लिंकेज (Linkage)", "अन्य (Other)"]

KNOWLEDGE_LEVELS = [
    "लोग जागरूक नहीं हैं और वित्तीय रूप से अशिक्षित हैं",
    "लोग जागरूक हैं और वित्तीय रूप से शिक्षित हैं",
    "लोग जागरूक हैं और हाल ही में वित्तीय रूप से शिक्षित हुए हैं (पिछले एक वर्ष की अवधि में)",
    "लोग जागरूक हैं और औपचारिक वित्तीय सेवाओं का उपयोग कर रहे हैं"
]

# -------------------- DATABASE --------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS camps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cbo_id TEXT,
            cbo_name TEXT,
            camp_type TEXT,
            camp_date TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_hh TEXT,
            duration_mm TEXT,
            village TEXT,
            gram_panchayat TEXT,
            block TEXT,
            district TEXT,
            trainer_name TEXT,
            trainer_designation TEXT,
            female_count INTEGER,
            male_count INTEGER,
            transgender_count INTEGER,
            total_participants INTEGER,
            group_type TEXT,
            training_method TEXT,
            topics TEXT,
            knowledge_level TEXT,
            phase TEXT,
            remarks TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS camp_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camp_id INTEGER,
            staff_id TEXT,
            staff_name TEXT,
            designation TEXT,
            present INTEGER DEFAULT 1,
            FOREIGN KEY (camp_id) REFERENCES camps(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camp_id INTEGER,
            name TEXT,
            father_husband TEXT,
            category TEXT,
            age INTEGER,
            occupation TEXT,
            education TEXT,
            mobile TEXT,
            linkage_type TEXT,
            FOREIGN KEY (camp_id) REFERENCES camps(id)
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect(DB_PATH)

# -------------------- DATA LOADING --------------------
@st.cache_data
def load_staff():
    df = pd.read_csv(STAFF_CSV)
    df['Mobile No'] = df['Mobile No'].astype(str)
    return df

@st.cache_data
def load_leaders():
    df = load_staff()
    # Leaders = anyone who has people reporting to them
    leader_ids = df['Primary_ID'].dropna().unique().tolist()
    leaders = df[df['Consultant No'].isin(leader_ids)][
        ['Consultant No', 'Consultant', 'Designation', 'Working Location', 'Mobile No']
    ].copy()
    leaders = leaders.sort_values('Consultant').reset_index(drop=True)
    return leaders

def get_team(cbo_id, staff_df):
    """Return all staff whose Primary_ID == cbo_id"""
    team = staff_df[staff_df['Primary_ID'] == cbo_id].copy()
    return team

# -------------------- AUTH --------------------
def login_page():
    st.title("🏦 MoneyWise – CBO Training Portal")
    st.markdown("### वित्तीय साक्षरता केंद्र | Capacity Building Officer Login")
    st.divider()

    leaders = load_leaders()
    leader_options = {
        f"{row['Consultant']} ({row['Consultant No']}) – {row['Working Location']}": row['Consultant No']
        for _, row in leaders.iterrows()
    }

    selected = st.selectbox("अपना नाम / CBO ID चुनें", options=list(leader_options.keys()))
    password = st.text_input("Password (default: cbo123)", type="password", value="cbo123")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Login", type="primary", use_container_width=True):
            if password == "cbo123":
                cbo_id = leader_options[selected]
                cbo_row = leaders[leaders['Consultant No'] == cbo_id].iloc[0]
                st.session_state['logged_in'] = True
                st.session_state['cbo_id'] = cbo_id
                st.session_state['cbo_name'] = cbo_row['Consultant']
                st.session_state['cbo_location'] = cbo_row['Working Location']
                st.session_state['cbo_designation'] = cbo_row['Designation']
                st.rerun()
            else:
                st.error("गलत Password। Default password: cbo123")

    st.info("💡 Demo Login: कोई भी CBO चुनें + Password: **cbo123**")

# -------------------- DASHBOARD --------------------
def dashboard(staff_df):
    cbo_id = st.session_state['cbo_id']
    cbo_name = st.session_state['cbo_name']
    team = get_team(cbo_id, staff_df)

    st.title(f"👋 नमस्ते, {cbo_name}")
    st.caption(f"{st.session_state['cbo_designation']} | {st.session_state['cbo_location']} | ID: {cbo_id}")
    st.divider()

    # KPI cards
    fc_count = len(team[team['Designation'].str.contains('Field Coordinator', na=False)])
    cm_count = len(team[team['Designation'].str.contains('Centre Manager', na=False)])
    deo_count = len(team[team['Designation'].str.contains('Data Entry Operator', na=False)])
    other_count = len(team) - fc_count - cm_count - deo_count

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("कुल टीम", len(team))
    k2.metric("Field Coordinator", fc_count)
    k3.metric("Centre Manager", cm_count)
    k4.metric("Data Entry Operator", deo_count)
    k5.metric("अन्य", other_count)

    # Recent camps
    conn = get_db()
    camps = pd.read_sql_query(
        "SELECT id, camp_date, camp_type, village, district, total_participants, phase FROM camps WHERE cbo_id=? ORDER BY camp_date DESC LIMIT 10",
        conn, params=(cbo_id,)
    )
    conn.close()

    st.subheader("📋 हाल की Camps / Training")
    if camps.empty:
        st.info("अभी तक कोई camp entry नहीं हुई है। बाईं तरफ से 'नया Camp / Training' चुनें।")
    else:
        st.dataframe(camps, use_container_width=True, hide_index=True)

# -------------------- STAFF LIST --------------------
def staff_list_page(staff_df):
    cbo_id = st.session_state['cbo_id']
    team = get_team(cbo_id, staff_df)

    st.title("👥 मेरी टीम (FC / CM / DEO)")
    st.caption(f"कुल {len(team)} सदस्य | CBO: {st.session_state['cbo_name']}")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        desig_filter = st.multiselect(
            "Designation",
            options=sorted(team['Designation'].unique()),
            default=sorted(team['Designation'].unique())
        )
    with col2:
        loc_filter = st.multiselect(
            "Working Location",
            options=sorted(team['Working Location'].dropna().unique()),
            default=[]
        )
    with col3:
        search = st.text_input("Search (Name / ID / Mobile)")

    filtered = team[team['Designation'].isin(desig_filter)]
    if loc_filter:
        filtered = filtered[filtered['Working Location'].isin(loc_filter)]
    if search:
        mask = (
            filtered['Consultant'].str.contains(search, case=False, na=False) |
            filtered['Consultant No'].str.contains(search, case=False, na=False) |
            filtered['Mobile No'].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    # Document status
    def doc_status(row):
        pending = []
        if str(row.get('Aadhar Card', '')).lower() != 'verified':
            pending.append('Aadhaar')
        if str(row.get('PAN Card', '')).lower() != 'verified':
            pending.append('PAN')
        if str(row.get('Bank Cancelled Cheque/Passbook', '')).lower() != 'verified':
            pending.append('Bank')
        if str(row.get('TDS Exemption Certificate', '')).lower() == 'pending':
            pending.append('TDS')
        return ', '.join(pending) if pending else '✅ All Verified'

    display = filtered[[
        'Consultant No', 'Consultant', 'Designation', 'Working Location',
        'Mobile No', 'Gender', 'Aging', 'BCC Code'
    ]].copy()
    display['Document Pending'] = filtered.apply(doc_status, axis=1)

    st.dataframe(display, use_container_width=True, hide_index=True, height=500)

    st.download_button(
        "📥 Excel Download",
        data=display.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"team_{cbo_id}_{date.today()}.csv",
        mime="text/csv"
    )

# -------------------- NEW CAMP / TRAINING ENTRY --------------------
def new_camp_page(staff_df):
    cbo_id = st.session_state['cbo_id']
    cbo_name = st.session_state['cbo_name']
    team = get_team(cbo_id, staff_df)

    st.title("📝 नया Camp / Training Entry")
    st.caption("Input Reporting Format के अनुसार")

    with st.form("camp_form", clear_on_submit=True):
        st.subheader("1. कैम्प की मूल जानकारी")
        c1, c2, c3 = st.columns(3)
        with c1:
            camp_type = st.selectbox("कैम्प प्रकार", CAMP_TYPES)
            camp_date = st.date_input("दिनांक", value=date.today())
        with c2:
            start_time = st.time_input("समय से")
            end_time = st.time_input("समय तक")
        with c3:
            duration_hh = st.number_input("अवधि (घंटे)", min_value=0, max_value=12, value=2)
            duration_mm = st.number_input("अवधि (मिनट)", min_value=0, max_value=59, value=0)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            village = st.text_input("ग्राम *")
        with c2:
            gram_panchayat = st.text_input("ग्राम पंचायत")
        with c3:
            block = st.text_input("ब्लॉक")
        with c4:
            district = st.text_input("जिला *")

        st.subheader("2. ट्रेनर जानकारी")
        t1, t2 = st.columns(2)
        with t1:
            trainer_name = st.text_input("ट्रेनर का नाम", value=cbo_name)
        with t2:
            trainer_desig = st.text_input("पद", value=st.session_state.get('cbo_designation', ''))

        st.subheader("3. प्रतिभागियों की संख्या")
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            female = st.number_input("महिला", min_value=0, value=0)
        with p2:
            male = st.number_input("पुरुष", min_value=0, value=0)
        with p3:
            trans = st.number_input("ट्रांसजेंडर", min_value=0, value=0)
        with p4:
            total = female + male + trans
            st.metric("कुल", total)

        st.subheader("4. समूह का प्रकार एवं पद्धति")
        g1, g2 = st.columns(2)
        with g1:
            group_type = st.selectbox("समूह का प्रकार", GROUP_TYPES)
        with g2:
            method = st.selectbox("प्रशिक्षण की पद्धति", TRAINING_METHODS)

        st.subheader("5. कैम्प के मुख्य विषय (Topics)")
        selected_topics = st.multiselect("विषय चुनें (PDF के अनुसार)", CAMP_TOPICS)

        knowledge = st.radio("उपस्थित समूह के लोगों की श्रेणी", KNOWLEDGE_LEVELS)

        phase = st.selectbox("Phase", ["Phase-II", "Phase-III", "Extension Phase - 1", "अन्य"])

        remarks = st.text_area("अतिरिक्त टिप्पणी / Remarks")

        st.subheader("6. स्टाफ Attendance (FC / CM / DEO)")
        st.caption("जिन स्टाफ ने इस camp में भाग लिया, उन्हें टिक करें")
        staff_options = {
            f"{row['Consultant']} ({row['Consultant No']}) – {row['Designation'].replace('Consultant (','').replace(')','')}": row['Consultant No']
            for _, row in team.iterrows()
        }
        present_staff = st.multiselect("उपस्थित स्टाफ", options=list(staff_options.keys()))

        submitted = st.form_submit_button("💾 Camp Save करें", type="primary", use_container_width=True)

        if submitted:
            if not village or not district:
                st.error("ग्राम और जिला अनिवार्य हैं।")
            elif total == 0:
                st.error("कम से कम 1 प्रतिभागी होना चाहिए।")
            else:
                conn = get_db()
                c = conn.cursor()
                c.execute("""
                    INSERT INTO camps (
                        cbo_id, cbo_name, camp_type, camp_date, start_time, end_time,
                        duration_hh, duration_mm, village, gram_panchayat, block, district,
                        trainer_name, trainer_designation, female_count, male_count,
                        transgender_count, total_participants, group_type, training_method,
                        topics, knowledge_level, phase, remarks, created_at
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    cbo_id, cbo_name, camp_type, str(camp_date),
                    str(start_time), str(end_time), str(duration_hh), str(duration_mm),
                    village, gram_panchayat, block, district,
                    trainer_name, trainer_desig, female, male, trans, total,
                    group_type, method, ", ".join(selected_topics), knowledge,
                    phase, remarks, datetime.now().isoformat()
                ))
                camp_id = c.lastrowid

                # Attendance
                for s in present_staff:
                    sid = staff_options[s]
                    srow = team[team['Consultant No'] == sid].iloc[0]
                    c.execute(
                        "INSERT INTO camp_attendance (camp_id, staff_id, staff_name, designation, present) VALUES (?,?,?,?,1)",
                        (camp_id, sid, srow['Consultant'], srow['Designation'])
                    )
                conn.commit()
                conn.close()
                st.success(f"✅ Camp successfully saved! (ID: {camp_id})")
                st.balloons()

# -------------------- REPORTS --------------------
def reports_page():
    cbo_id = st.session_state['cbo_id']
    st.title("📊 Reports & Indicators")

    conn = get_db()
    camps = pd.read_sql_query(
        "SELECT * FROM camps WHERE cbo_id=? ORDER BY camp_date DESC",
        conn, params=(cbo_id,)
    )
    attendance = pd.read_sql_query(
        """SELECT a.*, c.camp_date, c.village, c.camp_type 
           FROM camp_attendance a 
           JOIN camps c ON a.camp_id = c.id 
           WHERE c.cbo_id=?""",
        conn, params=(cbo_id,)
    )
    conn.close()

    if camps.empty:
        st.warning("अभी कोई data नहीं है। पहले Camp entry करें।")
        return

    # Summary KPIs
    st.subheader("Summary Indicators")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("कुल Camps", len(camps))
    c2.metric("कुल Participants", int(camps['total_participants'].sum()))
    c3.metric("Physical / Training", len(camps[camps['camp_type'].str.contains('प्रशिक्षण|Training', na=False)]))
    c4.metric("Awareness / Linkage", len(camps[~camps['camp_type'].str.contains('प्रशिक्षण|Training', na=False)]))

    # Phase wise
    st.subheader("Phase-wise Camp Count")
    phase_counts = camps['phase'].value_counts().reset_index()
    phase_counts.columns = ['Phase', 'Count']
    st.dataframe(phase_counts, use_container_width=True, hide_index=True)

    # Topic frequency
    st.subheader("Topics Coverage")
    all_topics = []
    for t in camps['topics'].dropna():
        all_topics.extend([x.strip() for x in str(t).split(',')])
    if all_topics:
        topic_df = pd.Series(all_topics).value_counts().reset_index()
        topic_df.columns = ['Topic', 'Times Covered']
        st.dataframe(topic_df, use_container_width=True, hide_index=True)

    # Full camp list
    st.subheader("सभी Camp Details")
    show_cols = ['id', 'camp_date', 'camp_type', 'village', 'district', 'total_participants',
                 'female_count', 'male_count', 'phase', 'topics']
    st.dataframe(camps[show_cols], use_container_width=True, hide_index=True)

    st.download_button(
        "📥 Full Report CSV",
        data=camps.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"camp_report_{cbo_id}_{date.today()}.csv",
        mime="text/csv"
    )

    if not attendance.empty:
        st.subheader("Staff Attendance Log")
        st.dataframe(attendance, use_container_width=True, hide_index=True)

# -------------------- MAIN --------------------
def main():
    st.set_page_config(
        page_title="CBO Training Portal | MoneyWise",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_db()
    staff_df = load_staff()

    # Custom CSS
    st.markdown("""
    <style>
        .stMetric { background: #f0f7ff; padding: 12px; border-radius: 10px; }
        div[data-testid="stSidebar"] { background: #e8f4f8; }
    </style>
    """, unsafe_allow_html=True)

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        login_page()
        return

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/bank.png", width=60)
        st.markdown(f"**{st.session_state['cbo_name']}**")
        st.caption(st.session_state['cbo_id'])
        st.divider()

        page = st.radio(
            "Navigation",
            ["🏠 Dashboard", "👥 मेरी टीम", "📝 नया Camp / Training", "📊 Reports"],
            label_visibility="collapsed"
        )
        st.divider()
        if st.button("Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    if page == "🏠 Dashboard":
        dashboard(staff_df)
    elif page == "👥 मेरी टीम":
        staff_list_page(staff_df)
    elif page == "📝 नया Camp / Training":
        new_camp_page(staff_df)
    elif page == "📊 Reports":
        reports_page()

if __name__ == "__main__":
    main()
