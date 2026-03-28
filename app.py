import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import time

# --- 1. CREDENTIALS ---
SUPABASE_URL = "https://bkaqwcwicmmaqzcuqtox.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrYXF3Y3dpY21tYXF6Y3VxdG94Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ2MzU3MzUsImV4cCI6MjA5MDIxMTczNX0.eISJsmmFBYVZS2vJhx8YjTW274I37V3Q_HY2f2RHw50"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

NVIDIA_API_KEY = "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" 
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)

# --- 2. SESSION STATE ---
if "theme" not in st.session_state: st.session_state.theme = "Dark"
if "role" not in st.session_state: st.session_state.role = "Doctor"
if "auth_status" not in st.session_state: st.session_state.auth_status = False
if "user_uuid" not in st.session_state: st.session_state.user_uuid = None

# --- 3. THEME ENGINE ---
if st.session_state.theme == "Dark":
    bg, txt, border = "#000000", "#FFFFFF", "#FFFFFF"
    theme_label = "☀️ Light Mode"
else:
    bg, txt, border = "#FFFFFF", "#000000", "#000000"
    theme_label = "🌙 Dark Mode"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; color: {txt} !important; }}
    h1, h2, h3, h4, h5, p, span, label, div, .stMarkdown {{ color: {txt} !important; opacity: 1 !important; -webkit-text-fill-color: {txt} !important; }}
    [data-testid="stSidebar"] {{ background-color: {bg} !important; border-right: 2px solid {border}; }}
    [data-testid="stSidebar"] * {{ color: {txt} !important; }}
    .report-card {{ background-color: {bg}; border: 3px solid {border} !important; padding: 25px; border-radius: 8px; margin-bottom: 20px; }}
    input, textarea, [data-baseweb="select"], [data-baseweb="input"] {{ background-color: {bg} !important; border: 2px solid {border} !important; color: {txt} !important; }}
    div[role="listbox"] {{ background-color: {bg} !important; color: {txt} !important; }}
    .stButton>button {{ background-color: {bg} !important; color: {txt} !important; border: 2px solid {border} !important; width: 100%; font-weight: bold; }}
    /* Hide the default submit button border to keep it clean */
    .stForm {{ border: none !important; padding: 0 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ CogniScan Control")
    if st.button(theme_label):
        st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
        st.rerun()
    st.divider()
    st.write(f"Portal: **{st.session_state.role} Mode**")
    if st.button(f"🔄 Switch to {'Patient' if st.session_state.role == 'Doctor' else 'Doctor'}"):
        st.session_state.role = "Patient" if st.session_state.role == "Doctor" else "Doctor"
        st.session_state.auth_status = False
        st.rerun()

# --- 5. UPDATED LOGIN LOGIC (With Enter-Key Support) ---
if not st.session_state.auth_status:
    st.title(f"👨‍⚕️ {st.session_state.role} Access")
    
    # Wrapping in a form enables the Enter key
    with st.form("login_form", clear_on_submit=False):
        email_in = st.text_input("Email", key="login_email")
        pass_in = st.text_input("Password", type="password", key="login_pass")
        submit_button = st.form_submit_button("Authorize")
        
        if submit_button:
            try:
                res = supabase.auth.sign_in_with_password({"email": email_in, "password": pass_in})
                st.session_state.auth_status = True
                st.session_state.user_uuid = res.user.id
                st.success("✅ Access Granted! Redirecting...")
                time.sleep(0.6)
                st.rerun()
            except Exception:
                st.error("❌ Invalid Credentials")

# --- 6. DOCTOR PORTAL ---
elif st.session_state.role == "Doctor":
    st.title("🧠 Cognitive Screening Suite")
    if st.button("⬅️ Log Out"):
        st.session_state.auth_status = False
        st.rerun()
    
    c1, c2, c3 = st.columns([2, 1, 1])
    p_id = c1.text_input("Patient ID", "NC-2026")
    p_age = c2.number_input("Age", 18, 110, 72)
    p_sex = c3.selectbox("Sex", ["Male", "Female", "Other"])
    
    p_history = st.text_area("Medical History", placeholder="Enter clinical background...")
    
    v_file = st.file_uploader("Upload Session Video", type=["mp4"])
    
    if v_file and st.button("🚀 Run Comprehensive Analysis"):
        with st.status("Analyzing via NVIDIA NIM..."):
            prompt = f"Neuro-screening for {p_age}yo {p_sex}. History: {p_history}. Use ###DOC### Technical Report and ###PAT### Family Guide."
            res = client.chat.completions.create(model="meta/llama-4-maverick-17b-128e-instruct", messages=[{"role":"user","content":prompt}])
            out = res.choices[0].message.content
            doc_rep = out.split("###DOC###")[-1].split("###PAT###")[0].strip()
            pat_rep = out.split("###PAT###")[-1].strip()
            
            try:
                supabase.table("patients").insert({
                    "user_id": st.session_state.user_uuid, "patient_id": p_id, "age": p_age, "doctor_report": doc_rep, "family_guide": pat_rep
                }).execute()
                st.success("✅ Analysis Synced to Cloud Database")
            except Exception:
                st.warning("⚠️ Local Analysis Complete (Cloud Sync Deferred)")

            st.markdown("### 📊 Physician Diagnostic Report")
            st.markdown(f"<div class='report-card'>{doc_rep}</div>", unsafe_allow_html=True)
            
            d1, d2 = st.columns(2)
            d1.download_button("📑 Download Tech Report", f"CLINICAL DOC: {p_id}\n\n{doc_rep}", f"Doc_{p_id}.txt")
            d2.download_button("🏡 Download Family Guide", f"FAMILY SUMMARY: {p_id}\n\n{pat_rep}", f"Family_{p_id}.txt")

# --- 7. PATIENT PORTAL ---
else:
    st.title("🏠 My Health Portal")
    if st.button("⬅️ Log Out"):
        st.session_state.auth_status = False
        st.rerun()

    try:
        res = supabase.table("patients").select("*").eq("user_id", st.session_state.user_uuid).order("created_at", descending=True).limit(1).execute()
        if res.data:
            report = res.data[0]
            st.markdown(f"### Update: {report['created_at'][:10]}")
            st.markdown(f"<div class='report-card'>{report['family_guide']}</div>", unsafe_allow_html=True)
            st.download_button("📥 Download My Summary", f"YOUR SUMMARY\n\n{report['family_guide']}", f"My_Report.txt")
        else:
            st.info("No records found for your account.")
    except Exception:
        st.error("Could not retrieve reports at this time.")

st.divider()
st.caption("© 2026 CogniScan | NVIDIA NIM Performance Architecture")