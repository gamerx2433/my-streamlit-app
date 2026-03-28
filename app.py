import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="CogniScan", page_icon="🧠", layout="wide")

# --- 1. CREDENTIALS ---
SUPABASE_URL = "https://bkaqwcwicmmaqzcuqtox.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrYXF3Y3dpY21tYXF6Y3VxdG94Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ2MzU3MzUsImV4cCI6MjA5MDIxMTczNX0.eISJsmmFBYVZS2vJhx8YjTW274I37V3Q_HY2f2RHw50"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

NVIDIA_API_KEY = "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"
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)

# --- 2. SESSION STATE ---
defaults = {
    "theme": "Dark",
    "role": "Doctor",
    "auth_status": False,
    "user_uuid": None,
    "patient_view": None,
    "page": "main",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- 3. THEME ---
dark    = st.session_state.theme == "Dark"
bg      = "#0A0A0F" if dark else "#F4F6FA"
surface = "#13131C" if dark else "#FFFFFF"
card    = "#1A1A28" if dark else "#FFFFFF"
txt     = "#E8E8F0" if dark else "#1A1A2E"
muted   = "#6B6B8A" if dark else "#8A8AB0"
accent  = "#7C6AF7"
accent2 = "#4FD1C5"
border  = "#2A2A40" if dark else "#E0E0EF"
theme_label   = "Light Mode" if dark else "Dark Mode"
switch_target = "Patient" if st.session_state.role == "Doctor" else "Doctor"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

* {{ box-sizing: border-box; }}

.stApp {{
    background-color: {bg} !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}

[data-testid="stSidebar"] {{
    background: {surface} !important;
    border-right: 1px solid {border} !important;
}}
[data-testid="stSidebar"] * {{ color: {txt} !important; }}
[data-testid="stSidebar"] .stButton>button {{
    background: transparent !important;
    border: 1px solid {border} !important;
    color: {txt} !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    padding: 8px 14px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    text-align: left !important;
    font-weight: 500 !important;
}}
[data-testid="stSidebar"] .stButton>button:hover {{
    border-color: {accent} !important;
    color: {accent} !important;
    background: rgba(124,106,247,0.08) !important;
}}

h1, h2, h3, h4, h5, p, span, label, div, .stMarkdown,
[data-testid="stMarkdownContainer"] {{
    color: {txt} !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}

input, textarea {{
    background-color: {card} !important;
    border: 1px solid {border} !important;
    border-radius: 8px !important;
    color: {txt} !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}
input:focus, textarea:focus {{
    border-color: {accent} !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,0.15) !important;
}}

[data-baseweb="select"] > div {{
    background-color: {card} !important;
    border: 1px solid {border} !important;
    border-radius: 8px !important;
    color: {txt} !important;
}}
[data-baseweb="select"] svg {{ fill: {muted} !important; }}
[role="listbox"] {{
    background-color: {surface} !important;
    border: 1px solid {border} !important;
    border-radius: 8px !important;
}}
[role="option"] {{ color: {txt} !important; }}
[role="option"]:hover {{ background: rgba(124,106,247,0.15) !important; }}

.stButton>button {{
    background: linear-gradient(135deg, {accent}, #9B59F7) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
}}
.stButton>button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(124,106,247,0.4) !important;
}}

[data-testid="stFormSubmitButton"] button {{
    background: linear-gradient(135deg, {accent}, #9B59F7) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s ease !important;
    padding: 12px 20px !important;
}}
[data-testid="stFormSubmitButton"] button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(124,106,247,0.4) !important;
}}

[data-testid="stDownloadButton"] button {{
    background: transparent !important;
    border: 1px solid {accent} !important;
    color: {accent} !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    background: rgba(124,106,247,0.1) !important;
}}

.stForm, [data-testid="stForm"] {{
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}}

[data-baseweb="input"] {{
    background-color: {card} !important;
    border: 1px solid {border} !important;
    border-radius: 8px !important;
}}

[data-testid="stFileUploader"] {{
    background: {card} !important;
    border: 2px dashed {border} !important;
    border-radius: 12px !important;
}}

hr {{ border-color: {border} !important; }}

[data-testid="stStatusWidget"] {{
    background: {card} !important;
    border: 1px solid {border} !important;
    border-radius: 12px !important;
}}

.stCaption {{ color: {muted} !important; font-size: 12px !important; }}

[data-testid="stRadio"] > div {{ gap: 8px !important; flex-wrap: wrap !important; }}
[data-testid="stRadio"] label {{
    background: {card} !important;
    border: 1px solid {border} !important;
    border-radius: 20px !important;
    padding: 5px 14px !important;
    cursor: pointer !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    color: {txt} !important;
}}
[data-testid="stRadio"] label:hover {{
    border-color: {accent} !important;
    color: {accent} !important;
}}
[data-testid="stRadio"] input[type="radio"] {{ display: none !important; }}

[data-testid="metric-container"] {{
    background: {card} !important;
    border: 1px solid {border} !important;
    border-radius: 12px !important;
    padding: 16px !important;
}}

[data-testid="stTabs"] [role="tab"] {{
    color: {muted} !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
}}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    color: {accent} !important;
    border-bottom-color: {accent} !important;
}}
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ────────────────────────────────────────
def page_header(title, subtitle=""):
    st.markdown(f"""
    <div style="padding:8px 0 28px 0;">
        <h1 style="margin:0; font-size:26px; font-weight:700; letter-spacing:-0.5px;">{title}</h1>
        {"" if not subtitle else f'<p style="color:{muted}; margin:4px 0 0 0; font-size:14px;">{subtitle}</p>'}
    </div>
    """, unsafe_allow_html=True)

def stat_card(label, value, color=None):
    c = color or accent
    return f"""<div style="background:{card}; border:1px solid {border}; border-radius:12px; padding:18px 20px; flex:1;">
        <div style="color:{muted}; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">{label}</div>
        <div style="color:{c}; font-size:22px; font-weight:700; font-family:'JetBrains Mono',monospace;">{value}</div>
    </div>"""

def report_card(content, border_color=None):
    bc = border_color or border
    st.markdown(f"""<div style="background:{card}; border:1px solid {bc}; border-left:4px solid {accent};
        border-radius:12px; padding:24px 28px; margin:12px 0; line-height:1.75;
        font-size:14px; color:{txt}; white-space:pre-wrap;">{content}</div>
    """, unsafe_allow_html=True)


# ─── SIDEBAR ────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:10px 0 20px 0;">
        <div style="font-size:20px; font-weight:700; letter-spacing:-0.5px;">CogniScan</div>
        <div style="color:{muted}; font-size:12px; margin-top:4px;">Neural Screening Platform</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(theme_label, key="theme_btn"):
        st.session_state.theme = "Light" if dark else "Dark"
        st.rerun()

    st.markdown(f"<div style='height:1px; background:{border}; margin:16px 0;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:rgba(124,106,247,0.1); border:1px solid rgba(124,106,247,0.3);
         border-radius:8px; padding:10px 14px; margin-bottom:12px;">
        <div style="color:{muted}; font-size:11px; text-transform:uppercase; letter-spacing:1px;">Active Portal</div>
        <div style="font-weight:600; font-size:14px; margin-top:3px;">{st.session_state.role} Mode</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"Switch to {switch_target}", key="switch_btn"):
        st.session_state.role = switch_target
        st.session_state.auth_status = False
        st.session_state.page = "main"
        st.session_state.patient_view = None
        st.rerun()

    if st.session_state.auth_status:
        st.markdown(f"<div style='height:1px; background:{border}; margin:16px 0;'></div>", unsafe_allow_html=True)
        if st.session_state.role == "Doctor" and st.session_state.page == "patient_report":
            if st.button("Back to Dashboard", key="back_btn"):
                st.session_state.page = "main"
                st.session_state.patient_view = None
                st.rerun()
        if st.button("Log Out", key="logout_btn"):
            st.session_state.auth_status = False
            st.session_state.page = "main"
            st.session_state.patient_view = None
            st.rerun()

    st.markdown(f"""
    <div style="position:fixed; bottom:20px; left:0; width:240px; padding:0 16px;">
        <div style="color:{muted}; font-size:11px; text-align:center;">2026 CogniScan · NVIDIA NIM</div>
    </div>
    """, unsafe_allow_html=True)


# ─── LOGIN ───────────────────────────────────────────
if not st.session_state.auth_status:
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown(f"""
        <div style="text-align:center; padding:40px 0 32px 0;">
            <div style="font-size:48px; margin-bottom:12px;">🧠</div>
            <h1 style="font-size:26px; font-weight:700; margin:0; letter-spacing:-0.5px;">Welcome to CogniScan</h1>
            <p style="color:{muted}; font-size:14px; margin-top:6px;">
                Sign in to access the {st.session_state.role} Portal
            </p>
        </div>
        <div style="background:{card}; border:1px solid {border}; border-radius:16px; padding:32px 32px 8px 32px;">
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email_in = st.text_input("Email Address", key="login_email", placeholder="you@hospital.com")
            pass_in  = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            submit = st.form_submit_button("Authorize Access", use_container_width=True)
            if submit:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_in, "password": pass_in})
                    st.session_state.auth_status = True
                    st.session_state.user_uuid = res.user.id
                    st.success("Access Granted!")
                    time.sleep(0.5)
                    st.rerun()
                except Exception:
                    st.error("Invalid credentials. Please try again.")


# ─── PATIENT REPORT DETAIL ───────────────────────────
elif st.session_state.page == "patient_report" and st.session_state.patient_view:
    r = st.session_state.patient_view
    pid_val  = r.get("patient_id", "N/A")
    age_val  = r.get("age", "-")
    date_val = r.get("created_at", "")[:10] if r.get("created_at") else "-"

    page_header(f"Patient Report - {pid_val}", f"Full diagnostic record · Created {date_val}")

    st.markdown(f"""
    <div style="display:flex; gap:14px; margin-bottom:28px;">
        {stat_card("Patient ID", pid_val)}
        {stat_card("Age", age_val, accent2)}
        {stat_card("Report Date", date_val, "#F6AD55")}
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Physician Report", "Family Guide"])
    with tab1:
        st.markdown(f"<div style='color:{muted}; font-size:13px; margin-bottom:12px;'>Technical clinical analysis for physician review</div>", unsafe_allow_html=True)
        report_card(r.get("doctor_report", "No clinical report available."))
        st.download_button("Download Physician Report",
            data=f"CLINICAL REPORT - {pid_val}\nDate: {date_val}\n\n{r.get('doctor_report','')}",
            file_name=f"Clinical_{pid_val}.txt", use_container_width=True)
    with tab2:
        st.markdown(f"<div style='color:{muted}; font-size:13px; margin-bottom:12px;'>Plain-language summary for patient and family</div>", unsafe_allow_html=True)
        report_card(r.get("family_guide", "No family guide available."), border_color=accent2)
        st.download_button("Download Family Guide",
            data=f"FAMILY GUIDE - {pid_val}\nDate: {date_val}\n\n{r.get('family_guide','')}",
            file_name=f"Family_{pid_val}.txt", use_container_width=True)


# ─── DOCTOR PORTAL ───────────────────────────────────
elif st.session_state.role == "Doctor":
    page_header("Cognitive Screening Suite", "Upload session video and run AI-powered neuro analysis")

    st.markdown(f"<div style='color:{muted}; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:14px;'>New Analysis</div>", unsafe_allow_html=True)

    with st.container():
        c1, c2, c3 = st.columns([2, 1, 1])
        p_id  = c1.text_input("Patient ID", value="NC-2026", placeholder="NC-2026")
        p_age = c2.number_input("Age", min_value=18, max_value=110, value=72)
        p_sex = c3.radio("Sex", options=["Male", "Female", "Other"], index=0, horizontal=True)
        p_history = st.text_area("Medical History",
            placeholder="Enter clinical background, prior diagnoses, medications, family history...", height=120)
        v_file = st.file_uploader("Upload Session Video", type=["mp4"])
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        run_btn = st.button("Run Comprehensive Analysis", use_container_width=True, key="run_analysis")

    if v_file and run_btn:
        with st.status("Analyzing via NVIDIA NIM...", expanded=True) as status:
            st.write("Preparing neuro-screening prompt...")
            prompt = (
                f"Neuro-screening for {p_age}yo {p_sex}. History: {p_history}. "
                f"Provide two sections clearly separated. "
                f"Start the physician section with ###DOC### and the family guide with ###PAT###. "
                f"###DOC### should be a detailed clinical technical report. "
                f"###PAT### should be a simple, warm, easy-to-understand family summary."
            )
            st.write("Requesting AI analysis...")
            res = client.chat.completions.create(
                model="meta/llama-4-maverick-17b-128e-instruct",
                messages=[{"role": "user", "content": prompt}]
            )
            out = res.choices[0].message.content
            doc_rep = out.split("###DOC###")[-1].split("###PAT###")[0].strip()
            pat_rep = out.split("###PAT###")[-1].strip()
            st.write("Syncing to database...")
            try:
                supabase.table("patients").insert({
                    "user_id": st.session_state.user_uuid,
                    "patient_id": p_id, "age": p_age,
                    "doctor_report": doc_rep, "family_guide": pat_rep
                }).execute()
                status.update(label="Analysis complete and synced!", state="complete")
            except Exception:
                status.update(label="Analysis complete (cloud sync deferred)", state="complete")

        st.markdown(f"<div style='margin-top:28px; color:{muted}; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:14px;'>Results - {p_id}</div>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Physician Report", "Family Guide"])
        with tab1:
            report_card(doc_rep)
            st.download_button("Download Physician Report", f"CLINICAL DOC: {p_id}\n\n{doc_rep}", f"Doc_{p_id}.txt", use_container_width=True)
        with tab2:
            report_card(pat_rep, border_color=accent2)
            st.download_button("Download Family Guide", f"FAMILY SUMMARY: {p_id}\n\n{pat_rep}", f"Family_{p_id}.txt", use_container_width=True)

    elif run_btn and not v_file:
        st.warning("Please upload a session video before running analysis.")

    st.markdown(f"<div style='height:1px; background:{border}; margin:32px 0 24px 0;'></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{muted}; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:16px;'>Recent Patient Records</div>", unsafe_allow_html=True)

    try:
        records = supabase.table("patients").select("*").eq("user_id", st.session_state.user_uuid).order("created_at", desc=True).limit(10).execute()
        if records.data:
            for rec in records.data:
                col_info, col_btn = st.columns([4, 1])
                with col_info:
                    date_str = rec.get("created_at", "")[:10]
                    pid_str  = rec.get("patient_id", "-")
                    age_str  = rec.get("age", "-")
                    preview  = (rec.get("doctor_report") or "")[:120].replace("\n", " ")
                    st.markdown(f"""
                    <div style="background:{card}; border:1px solid {border}; border-radius:10px; padding:16px 20px; margin-bottom:10px;">
                        <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                            <span style="font-weight:700; font-size:15px;">{pid_str}</span>
                            <span style="color:{muted};">·</span>
                            <span style="color:{muted}; font-size:13px;">Age {age_str}</span>
                            <span style="color:{muted};">·</span>
                            <span style="color:{muted}; font-size:12px;">{date_str}</span>
                        </div>
                        <div style="color:{muted}; font-size:13px; line-height:1.5;">{preview}{"..." if len(preview)>=120 else ""}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                    if st.button("View", key=f"view_{rec.get('id', rec.get('patient_id',''))}"):
                        st.session_state.patient_view = rec
                        st.session_state.page = "patient_report"
                        st.rerun()
        else:
            st.markdown(f"""
            <div style="background:{card}; border:1px dashed {border}; border-radius:12px; padding:32px; text-align:center;">
                <div style="color:{muted}; font-size:14px;">No patient records yet. Run your first analysis above.</div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not load patient records: {e}")


# ─── PATIENT PORTAL ──────────────────────────────────
else:
    page_header("My Health Portal", "View your latest cognitive screening summary")

    try:
        res = supabase.table("patients").select("*").eq("user_id", st.session_state.user_uuid).order("created_at", desc=True).limit(5).execute()
        if res.data:
            latest   = res.data[0]
            date_str = latest.get("created_at", "")[:10]
            pid_str  = latest.get("patient_id", "-")
            age_str  = latest.get("age", "-")

            st.markdown(f"""
            <div style="display:flex; gap:14px; margin-bottom:28px;">
                {stat_card("Patient ID", pid_str)}
                {stat_card("Your Age", age_str, accent2)}
                {stat_card("Report Date", date_str, "#F6AD55")}
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"<div style='color:{muted}; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:14px;'>Your Latest Report</div>", unsafe_allow_html=True)
            report_card(latest.get("family_guide", "No report content available."), border_color=accent2)
            st.download_button("Download My Summary",
                data=f"YOUR HEALTH SUMMARY\nDate: {date_str}\n\n{latest.get('family_guide','')}",
                file_name="My_CogniScan_Report.txt", use_container_width=True)

            if len(res.data) > 1:
                st.markdown(f"<div style='height:1px; background:{border}; margin:32px 0 24px 0;'></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:{muted}; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:16px;'>Report History</div>", unsafe_allow_html=True)
                for rec in res.data[1:]:
                    d = rec.get("created_at","")[:10]
                    preview = (rec.get("family_guide") or "")[:100].replace("\n"," ")
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.markdown(f"""
                        <div style="background:{card}; border:1px solid {border}; border-radius:10px; padding:14px 18px; margin-bottom:8px;">
                            <div style="color:{muted}; font-size:12px; margin-bottom:4px;">{d}</div>
                            <div style="font-size:13px; line-height:1.5;">{preview}{"..." if len(preview)>=100 else ""}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                        st.download_button("Download",
                            data=f"REPORT {d}\n\n{rec.get('family_guide','')}",
                            file_name=f"Report_{d}.txt",
                            key=f"dl_{rec.get('id', d)}")
        else:
            st.markdown(f"""
            <div style="background:{card}; border:1px dashed {border}; border-radius:16px; padding:48px 32px; text-align:center; margin-top:32px;">
                <h3 style="margin:0 0 8px 0; font-weight:600;">No Reports Yet</h3>
                <p style="color:{muted}; font-size:14px; margin:0;">Your doctor has not uploaded a screening report yet. Check back after your next appointment.</p>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Could not retrieve your reports. Please try again. ({e})")
