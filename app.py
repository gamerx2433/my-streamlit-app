import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import time

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CogniScan · Neural Screening",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CREDENTIALS (move to st.secrets in production) ─────────────────────────────
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://bkaqwcwicmmaqzcuqtox.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "YOUR_KEY_HERE")
NVIDIA_API_KEY = st.secrets.get("NVIDIA_API_KEY", "YOUR_KEY_HERE")

@st.cache_resource
def init_clients():
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    ai = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)
    return sb, ai

supabase, ai_client = init_clients()

# ─── SESSION STATE ───────────────────────────────────────────────────────────────
DEFAULTS = {
    "theme":        "Dark",
    "role":         "Doctor",
    "auth_status":  False,
    "user_uuid":    None,
    "patient_view": None,
    "page":         "main",
    "analysis":     None,   # holds latest analysis result
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── THEME TOKENS ────────────────────────────────────────────────────────────────
dark = st.session_state.theme == "Dark"

THEME = {
    "bg":      "#07070E" if dark else "#F0F2F8",
    "surface": "#0F0F1A" if dark else "#FFFFFF",
    "card":    "#161625" if dark else "#FFFFFF",
    "txt":     "#EAEAF5" if dark else "#12122A",
    "muted":   "#5C5C80" if dark else "#8080A8",
    "border":  "#252540" if dark else "#DCDCF0",
    "accent":  "#7C6AF7",
    "accent2": "#4FD1C5",
    "warn":    "#F6AD55",
    "danger":  "#FC8181",
    "success": "#68D391",
}
T = THEME  # shorthand

# ─── GLOBAL STYLES ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; }}

.stApp {{
    background: {T['bg']} !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {T['surface']} !important;
    border-right: 1px solid {T['border']} !important;
}}
[data-testid="stSidebar"] * {{ color: {T['txt']} !important; font-family: 'Inter', sans-serif !important; }}
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    border: 1px solid {T['border']} !important;
    color: {T['txt']} !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    padding: 8px 14px !important;
    width: 100% !important;
    text-align: left !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: {T['accent']} !important;
    color: {T['accent']} !important;
    background: rgba(124,106,247,0.08) !important;
}}

/* ── Typography ── */
h1, h2, h3, h4, h5, p, span, label, div,
.stMarkdown, [data-testid="stMarkdownContainer"] {{
    color: {T['txt']} !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Inputs ── */
input, textarea {{
    background: {T['card']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 8px !important;
    color: {T['txt']} !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}
input:focus, textarea:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,0.18) !important;
    outline: none !important;
}}
[data-baseweb="input"] {{
    background: {T['card']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 8px !important;
}}

/* ── Select / Dropdown ── */
[data-baseweb="select"] > div {{
    background: {T['card']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 8px !important;
    color: {T['txt']} !important;
}}
[data-baseweb="select"] svg {{ fill: {T['muted']} !important; }}
[role="listbox"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 10px !important;
}}
[role="option"] {{ color: {T['txt']} !important; }}
[role="option"]:hover {{ background: rgba(124,106,247,0.12) !important; }}

/* ── Primary Buttons ── */
.stButton > button {{
    background: linear-gradient(135deg, {T['accent']}, #9B59F7) !important;
    color: #FFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
    letter-spacing: 0.2px !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(124,106,247,0.45) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* ── Form Submit ── */
[data-testid="stFormSubmitButton"] button {{
    background: linear-gradient(135deg, {T['accent']}, #9B59F7) !important;
    color: #FFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: 0.4px !important;
    padding: 12px 20px !important;
    transition: all 0.2s !important;
}}
[data-testid="stFormSubmitButton"] button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(124,106,247,0.45) !important;
}}

/* ── Download Button ── */
[data-testid="stDownloadButton"] button {{
    background: transparent !important;
    border: 1px solid {T['accent']} !important;
    color: {T['accent']} !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    background: rgba(124,106,247,0.1) !important;
    transform: translateY(-1px) !important;
}}

/* ── Forms ── */
.stForm, [data-testid="stForm"] {{
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {{
    background: {T['card']} !important;
    border: 2px dashed {T['border']} !important;
    border-radius: 12px !important;
    transition: border-color 0.2s !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: {T['accent']} !important;
}}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {{
    color: {T['muted']} !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 10px 18px !important;
}}
[data-testid="stTabs"] [role="tab"] [aria-selected="true"] {{
    color: {T['accent']} !important;
    border-bottom: 2px solid {T['accent']} !important;
}}

/* ── Metrics ── */
[data-testid="metric-container"] {{
    background: {T['card']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 12px !important;
    padding: 16px !important;
}}

/* ── Misc ── */
hr {{ border-color: {T['border']} !important; }}
.stCaption {{ color: {T['muted']} !important; font-size: 12px !important; }}
[data-testid="stRadio"] > div {{ gap: 8px !important; flex-wrap: wrap !important; }}
[data-testid="stRadio"] label {{
    background: {T['card']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 20px !important;
    padding: 5px 14px !important;
    cursor: pointer !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
}}
[data-testid="stRadio"] label:hover {{
    border-color: {T['accent']} !important;
    color: {T['accent']} !important;
}}
[data-testid="stRadio"] input[type="radio"] {{ display: none !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {T['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {T['border']}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {T['muted']}; }}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    border-radius: 10px !important;
    border: none !important;
}}
</style>
""", unsafe_allow_html=True)


# ─── UI COMPONENTS ───────────────────────────────────────────────────────────────
def page_header(title: str, subtitle: str = ""):
    sub_html = f'<p style="color:{T["muted"]}; margin:5px 0 0 0; font-size:14px; font-weight:400;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="padding: 4px 0 28px 0; border-bottom: 1px solid {T['border']}; margin-bottom: 28px;">
        <h1 style="font-size:24px; font-weight:700; letter-spacing:-0.5px; margin:0;">{title}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def stat_card(label: str, value: str, color: str = None) -> str:
    c = color or T["accent"]
    return f"""
    <div style="background:{T['card']}; border:1px solid {T['border']}; border-radius:12px;
                padding:18px 22px; flex:1; min-width:120px;">
        <div style="color:{T['muted']}; font-size:10px; font-weight:600;
                    text-transform:uppercase; letter-spacing:1.2px; margin-bottom:8px;">{label}</div>
        <div style="color:{c}; font-size:22px; font-weight:700;
                    font-family:'JetBrains Mono',monospace; letter-spacing:-0.5px;">{value}</div>
    </div>"""


def report_card(content: str, border_color: str = None):
    bc = border_color or T["accent"]
    st.markdown(f"""
    <div style="background:{T['card']}; border:1px solid {T['border']}; border-left:4px solid {bc};
                border-radius:12px; padding:24px 28px; margin:12px 0;
                line-height:1.8; font-size:14px; color:{T['txt']}; white-space:pre-wrap;
                box-shadow:0 2px 12px rgba(0,0,0,0.15);">
        {content}
    </div>
    """, unsafe_allow_html=True)


def badge(text: str, color: str = None) -> str:
    c = color or T["accent"]
    return f"""<span style="background:rgba(124,106,247,0.12); color:{c}; border:1px solid {c}40;
                border-radius:20px; padding:2px 10px; font-size:11px; font-weight:600;
                letter-spacing:0.5px;">{text}</span>"""


def divider(margin: str = "28px 0"):
    st.markdown(f"<div style='height:1px; background:{T['border']}; margin:{margin};'></div>",
                unsafe_allow_html=True)


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown(f"""
    <div style="padding:16px 0 24px 0;">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="font-size:28px; line-height:1;">🧠</div>
            <div>
                <div style="font-size:18px; font-weight:700; letter-spacing:-0.5px;">CogniScan</div>
                <div style="color:{T['muted']}; font-size:11px; margin-top:1px;">Neural Screening Platform</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Active role badge
    role_color = T["accent"] if st.session_state.role == "Doctor" else T["accent2"]
    st.markdown(
