import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

CATEGORY_ICONS = {
    "Bathroom & Hygiene":         "🚿",
    "Anti-Ragging & Safety":      "🛡️",
    "Mess & Food Quality":        "🍽️",
    "Academic Issues":            "📖",
    "Infrastructure/Maintenance": "🔧",
    "Other":                      "📋",
}

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CampusGriev — Student Grievance Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --navy:      #0B1E3F;
  --navy-mid:  #132a52;
  --navy-light:#1e3a6e;
  --amber:     #D97706;
  --amber-lt:  #FEF3C7;
  --green:     #059669;
  --green-lt:  #D1FAE5;
  --red:       #DC2626;
  --red-lt:    #FEE2E2;
  --blue:      #2563EB;
  --blue-lt:   #DBEAFE;
  --border:    #E2E8F0;
  --white:     #FFFFFF;
  --text:      #0F172A;
  --text-mid:  #334155;
  --text-soft: #64748B;
  --slate-lt:  #F1F5F9;
  --radius:    10px;
  --shadow:    0 1px 3px rgba(0,0,0,.08), 0 4px 16px rgba(0,0,0,.04);
  --shadow-md: 0 4px 12px rgba(0,0,0,.10), 0 12px 32px rgba(0,0,0,.06);
}

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
  font-family: 'DM Sans', sans-serif !important;
  background: #F8FAFC !important;
  color: var(--text) !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarNav"],
button[title="View fullscreen"],
.stDeployButton { display: none !important; }

[data-testid="stSidebar"] { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }

/* Nav */
.topnav {
  background: var(--navy);
  padding: 0 2.5rem;
  display: flex; align-items: center; justify-content: space-between;
  height: 64px;
  border-bottom: 3px solid var(--amber);
  box-shadow: 0 2px 20px rgba(0,0,0,.25);
}
.topnav-brand { display: flex; align-items: center; gap: 12px; }
.topnav-logo {
  width: 38px; height: 38px;
  background: var(--amber); border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; font-weight: 700; color: var(--navy);
  font-family: 'DM Serif Display', serif;
}
.topnav-name { font-family: 'DM Serif Display', serif; font-size: 1.2rem; color: white; }
.topnav-sub  { font-size: 0.63rem; color: #94A3B8; letter-spacing: .08em; text-transform: uppercase; }
.status-pill {
  display: flex; align-items: center; gap: 6px;
  font-size: .73rem; color: #94A3B8;
}
.sdot { width: 7px; height: 7px; border-radius: 50%; background: #10B981; animation: blink 2s infinite; }
.sdot.off { background: #EF4444; animation: none; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.5} }

/* Tab nav */
.page-tabs {
  background: white; border-bottom: 1px solid var(--border);
  padding: 0 2.5rem; display: flex; gap: 0;
}
.ptab {
  padding: .85rem 1.3rem; font-size: .81rem; font-weight: 600;
  color: var(--text-soft); border-bottom: 3px solid transparent;
  font-family: 'DM Sans', sans-serif; background: none;
  border-top: none; border-left: none; border-right: none;
  cursor: pointer; white-space: nowrap; transition: all .15s;
}
.ptab:hover { color: var(--navy); background: var(--slate-lt); }
.ptab.active { color: var(--navy); border-bottom-color: var(--amber); }

/* hero */
.hero {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
  padding: 2.8rem 2.5rem; position: relative; overflow: hidden;
}
.hero::before {
  content: ''; position: absolute; top: -60px; right: -60px;
  width: 280px; height: 280px; background: var(--amber); opacity: .06; border-radius: 50%;
}
.hero-inner { max-width: 1100px; margin: 0 auto; position: relative; z-index: 1; }
.hero-eyebrow { font-size: .68rem; text-transform: uppercase; letter-spacing: .15em; color: var(--amber); font-weight: 600; margin-bottom: .6rem; }
.hero h1 { font-family: 'DM Serif Display', serif; font-size: 2rem; color: white; line-height: 1.15; margin-bottom: .5rem; }
.hero p  { font-size: .9rem; color: #94A3B8; max-width: 500px; line-height: 1.6; margin-bottom: 1.25rem; }
.hero-stats { display: flex; gap: 2rem; }
.hs-num   { font-family: 'DM Serif Display', serif; font-size: 1.4rem; color: var(--amber); }
.hs-label { font-size: .68rem; color: #94A3B8; text-transform: uppercase; letter-spacing: .06em; }

/* page body */
.page-body { max-width: 1100px; margin: 0 auto; padding: 1.8rem 2.5rem 4rem; }

/* admin hero */
.admin-hero {
  background: var(--navy); padding: 1.4rem 2.5rem;
  border-bottom: 3px solid var(--amber);
}
.admin-hero-inner { max-width: 1100px; margin: 0 auto; }
.ah-eye { font-size: .63rem; letter-spacing: .12em; color: var(--amber); text-transform: uppercase; font-weight: 700; margin-bottom: 3px; }
.ah-title { font-family: 'DM Serif Display', serif; font-size: 1.5rem; color: white; }
.ah-sub { font-size: .8rem; color: #64748B; margin-top: 3px; }

/* section */
.sec-title { font-family: 'DM Serif Display', serif; font-size: 1.35rem; color: var(--navy); margin-bottom: .2rem; }
.sec-sub   { font-size: .8rem; color: var(--text-soft); margin-bottom: 1.3rem; }

/* card */
.card { background: white; border: 1px solid var(--border); border-radius: var(--radius); padding: 1.4rem; box-shadow: var(--shadow); }
.card-hdr { font-size: .68rem; text-transform: uppercase; letter-spacing: .1em; font-weight: 700; color: var(--text-soft); margin-bottom: .9rem; padding-bottom: .7rem; border-bottom: 1px solid var(--border); }

/* metrics */
.mtr-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.4rem; }
.mtr-card { background: white; border: 1px solid var(--border); border-radius: var(--radius); padding: 1.1rem 1.3rem; box-shadow: var(--shadow); }
.mtr-label { font-size: .67rem; text-transform: uppercase; letter-spacing: .1em; color: var(--text-soft); font-weight: 600; margin-bottom: .35rem; }
.mtr-num { font-family: 'DM Serif Display', serif; font-size: 1.9rem; color: var(--navy); line-height: 1; }
.mtr-sub { font-size: .7rem; color: var(--text-soft); margin-top: 3px; }
.ml-amber { border-left: 3px solid var(--amber); }
.ml-green { border-left: 3px solid var(--green); }
.ml-blue  { border-left: 3px solid var(--blue); }
.ml-red   { border-left: 3px solid var(--red); }

/* badges */
.badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px; border-radius: 99px; font-size: .71rem; font-weight: 700; letter-spacing: .03em; }
.b-sub { background: #DBEAFE; color: #1D4ED8; }
.b-prg { background: #FEF3C7; color: #92400E; }
.b-res { background: #D1FAE5; color: #065F46; }
.b-rej { background: #FEE2E2; color: #991B1B; }

/* tracking card */
.trk-card { background: white; border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow-md); }
.trk-hdr  { background: var(--navy); padding: 1.2rem 1.4rem; display: flex; align-items: center; justify-content: space-between; }
.trk-id-lbl { font-size: .63rem; color: #64748B; text-transform: uppercase; letter-spacing: .1em; }
.trk-id-val { font-family: 'JetBrains Mono', monospace; font-size: 1.2rem; color: var(--amber); font-weight: 600; }
.trk-body { padding: 1.4rem; }
.trk-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .9rem; margin-bottom: 1.1rem; }
.tg-lbl { font-size: .68rem; text-transform: uppercase; letter-spacing: .07em; color: var(--text-soft); font-weight: 600; margin-bottom: 2px; }
.tg-val { font-size: .88rem; color: var(--text); font-weight: 500; }

/* timeline */
.timeline { display: flex; align-items: center; margin: 1.1rem 0; }
.tl-dot { width: 26px; height: 26px; border-radius: 50%; background: var(--border); border: 2px solid var(--border); display: flex; align-items: center; justify-content: center; font-size: .68rem; font-weight: 700; color: var(--text-soft); flex-shrink: 0; }
.tl-dot.done    { background: var(--navy);  border-color: var(--navy);  color: white; }
.tl-dot.current { background: var(--amber); border-color: var(--amber); color: white; }
.tl-lbl { font-size: .69rem; font-weight: 600; margin-left: 5px; color: var(--text-soft); white-space: nowrap; }
.tl-lbl.done    { color: var(--navy); }
.tl-lbl.current { color: var(--amber); }
.tl-line { flex: 1; height: 2px; background: var(--border); min-width: 20px; }
.tl-line.done { background: var(--navy); }

/* alerts */
.alert { padding: .8rem 1rem; border-radius: 8px; font-size: .83rem; margin: .6rem 0; display: flex; gap: 9px; align-items: flex-start; line-height: 1.5; }
.a-ok   { background: #D1FAE5; color: #065F46; border: 1px solid #6EE7B7; }
.a-err  { background: #FEE2E2; color: #7F1D1D; border: 1px solid #FCA5A5; }
.a-info { background: #DBEAFE; color: #1E3A8A; border: 1px solid #93C5FD; }
.a-warn { background: #FEF3C7; color: #78350F; border: 1px solid #FCD34D; }

/* conf bar */
.conf-wrap { display: flex; align-items: center; gap: 8px; }
.conf-bg   { flex: 1; height: 5px; background: var(--slate-lt); border-radius: 99px; overflow: hidden; }
.conf-fill { height: 100%; border-radius: 99px; }
.conf-pct  { font-size: .7rem; font-weight: 600; color: var(--text-soft); min-width: 26px; }

/* cat grid */
.cat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: .65rem; margin-top: .9rem; }
.cat-card { background: var(--slate-lt); border: 1px solid var(--border); border-radius: 8px; padding: .75rem; }
.cat-icon { font-size: 1rem; margin-bottom: 3px; }
.cat-name { font-weight: 600; font-size: .76rem; color: var(--navy); }
.cat-dept { font-size: .68rem; color: var(--text-soft); margin-top: 1px; }

/* how it works */
.step { display: flex; gap: 11px; align-items: flex-start; }
.step-num { width: 24px; height: 24px; border-radius: 50%; background: var(--navy); color: white; display: flex; align-items: center; justify-content: center; font-size: .68rem; font-weight: 700; flex-shrink: 0; }
.step-num.last { background: var(--amber); }
.step-title { font-weight: 600; font-size: .83rem; color: var(--navy); }
.step-desc  { font-size: .76rem; color: var(--text-soft); margin-top: 1px; }

/* bar chart rows */
.bar-row { margin-bottom: .85rem; }
.bar-top  { display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px; }
.bar-name { font-size: .81rem; font-weight: 600; color: var(--text); }
.bar-cnt  { font-size: .76rem; color: var(--text-soft); }
.bar-bg   { background: var(--slate-lt); border-radius: 99px; height: 6px; }
.bar-fill { height: 6px; border-radius: 99px; }

/* status block */
.sb-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: .9rem; }
.sb-card { text-align: center; padding: .9rem; background: var(--slate-lt); border-radius: 8px; border: 1px solid var(--border); }
.sb-num { font-family: 'DM Serif Display', serif; font-size: 1.7rem; line-height: 1; }
.sb-lbl { font-size: .73rem; font-weight: 600; color: var(--text-mid); margin: 2px 0; }
.sb-pct { font-size: .68rem; color: var(--text-soft); }

/* divider */
.div { border: none; border-top: 1px solid var(--border); margin: 1.25rem 0; }

/* streamlit overrides */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label {
  font-size: .76rem !important; font-weight: 600 !important; color: var(--text-mid) !important;
  text-transform: uppercase !important; letter-spacing: .06em !important;
  font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  border: 1.5px solid var(--border) !important; border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important; font-size: .89rem !important;
  color: var(--text) !important; background: white !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--navy) !important;
  box-shadow: 0 0 0 3px rgba(11,30,63,.08) !important; outline: none !important;
}
[data-testid="stFormSubmitButton"] button,
.stButton > button {
  background: var(--navy) !important; color: white !important;
  border: none !important; border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
  font-size: .84rem !important; letter-spacing: .02em !important;
  transition: all .15s !important;
  box-shadow: 0 2px 6px rgba(11,30,63,.22) !important;
}
[data-testid="stFormSubmitButton"] button:hover,
.stButton > button:hover {
  background: var(--navy-light) !important;
  transform: translateY(-1px) !important;
}
[data-testid="stSelectbox"] > div > div {
  border: 1.5px solid var(--border) !important; border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important; border-radius: var(--radius) !important;
  box-shadow: var(--shadow) !important; background: white !important;
  margin-bottom: .5rem !important;
}
[data-testid="stExpander"] summary {
  font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
  font-size: .83rem !important; color: var(--text) !important; padding: .8rem 1rem !important;
}
.stForm { border: none !important; padding: 0 !important; background: none !important; }
[data-testid="stVerticalBlock"] > div { margin-bottom: 0 !important; }

/* footer */
.portal-footer {
  background: var(--navy); color: #475569; text-align: center;
  padding: 1.4rem; font-size: .73rem; margin-top: 3rem; letter-spacing: .02em;
}
.portal-footer span { color: #94A3B8; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  STATE & HELPERS
# ══════════════════════════════════════════════════════════════════════════════
if "page"         not in st.session_state: st.session_state.page = "submit"
if "admin_auth"   not in st.session_state: st.session_state.admin_auth = False
if "submit_result"not in st.session_state: st.session_state.submit_result = None

def api_get(ep, params=None):
    try:
        r = requests.get(f"{BACKEND_URL}{ep}", params=params, timeout=15)
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500

def api_post(ep, body):
    try:
        r = requests.post(f"{BACKEND_URL}{ep}", json=body, timeout=30)
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500

def api_put(ep, body):
    try:
        r = requests.put(f"{BACKEND_URL}{ep}", json=body, timeout=15)
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500

def sbadge(status):
    cls = {"Submitted":"b-sub","In Progress":"b-prg","Resolved":"b-res","Rejected":"b-rej"}.get(status,"b-sub")
    dot = {"Submitted":"●","In Progress":"◐","Resolved":"✓","Rejected":"✕"}.get(status,"●")
    return f'<span class="badge {cls}">{dot} {status}</span>'

def cbar(score):
    p = int(score * 100)
    c = "#059669" if p >= 75 else "#D97706" if p >= 50 else "#DC2626"
    return f'<div class="conf-wrap"><div class="conf-bg"><div class="conf-fill" style="width:{p}%;background:{c}"></div></div><span class="conf-pct">{p}%</span></div>'

# Backend check
backend_ok = False
try:
    _, _c = api_get("/")
    backend_ok = (_c == 200)
except: pass

# Stats for hero
hero_total = hero_res = hero_pend = 0
try:
    sd, sc = api_get("/admin/stats")
    if sc == 200:
        hero_total = sd.get("total", 0)
        hero_res   = sd.get("by_status", {}).get("Resolved", 0)
        hero_pend  = sd.get("by_status", {}).get("Submitted", 0) + sd.get("by_status", {}).get("In Progress", 0)
except: pass

# ══════════════════════════════════════════════════════════════════════════════
#  NAVBAR
# ══════════════════════════════════════════════════════════════════════════════
dot = "sdot" if backend_ok else "sdot off"
dot_txt = "System Operational" if backend_ok else "System Offline"
st.markdown(f"""
<div class="topnav">
  <div class="topnav-brand">
    <div class="topnav-logo">CG</div>
    <div>
      <div class="topnav-name">CampusGriev</div>
      <div class="topnav-sub">Student Grievance Portal</div>
    </div>
  </div>
  <div class="status-pill">
    <div class="{dot}"></div>
    <span>{dot_txt}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB BAR
# ══════════════════════════════════════════════════════════════════════════════
tabs_def = [
    ("submit", "📝  Submit Grievance"),
    ("track",  "🔍  Track Status"),
    ("admin",  "🛠  Admin Panel"),
    ("stats",  "📊  Statistics"),
]
pg = st.session_state.page
tab_html = '<div class="page-tabs">'
for k, lbl in tabs_def:
    ac = "active" if pg == k else ""
    tab_html += f'<span class="ptab {ac}">{lbl}</span>'
tab_html += "</div>"
st.markdown(tab_html, unsafe_allow_html=True)

# Real invisible buttons
btn_cols = st.columns(len(tabs_def))
for i, (k, lbl) in enumerate(tabs_def):
    with btn_cols[i]:
        if st.button(lbl, key=f"tb_{k}"):
            st.session_state.page = k
            st.rerun()
st.markdown("""<style>
div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button {
  opacity:0!important;height:2px!important;padding:0!important;
  min-height:0!important;margin-top:-34px!important;
  border-radius:0!important;box-shadow:none!important;
}
</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
if pg in ("submit","track"):
    hero_map = {
        "submit": ("RAISE A COMPLAINT",  "Submit Your Grievance",
                   "Facing a problem on campus? Describe it below. Our AI classifies and routes it instantly."),
        "track":  ("TRACK YOUR COMPLAINT","Check Grievance Status",
                   "Enter your unique Tracking ID to see real-time updates on your complaint."),
    }
    ey, h1, p = hero_map[pg]
    st.markdown(f"""
    <div class="hero">
      <div class="hero-inner">
        <div class="hero-eyebrow">{ey}</div>
        <h1>{h1}</h1>
        <p>{p}</p>
        <div class="hero-stats">
          <div><div class="hs-num">{hero_total}</div><div class="hs-label">Total Complaints</div></div>
          <div><div class="hs-num">{hero_res}</div><div class="hs-label">Resolved</div></div>
          <div><div class="hs-num">{hero_pend}</div><div class="hs-label">Pending</div></div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE — SUBMIT
# ══════════════════════════════════════════════════════════════════════════════
if pg == "submit":
    st.markdown('<div class="page-body">', unsafe_allow_html=True)
    left, right = st.columns([3, 2], gap="large")

    with left:
        if st.session_state.submit_result:
            d = st.session_state.submit_result
            st.markdown(f"""
            <div class="trk-card" style="margin-bottom:1.2rem">
              <div class="trk-hdr">
                <div>
                  <div class="trk-id-lbl">Your Tracking ID — save this</div>
                  <div class="trk-id-val">{d['tracking_id']}</div>
                </div>
                {sbadge("Submitted")}
              </div>
              <div class="trk-body">
                <div class="alert a-ok" style="margin-bottom:.9rem">
                  ✅ Complaint submitted and routed to <strong>{d['department']}</strong>.
                </div>
                <div class="trk-grid">
                  <div><div class="tg-lbl">AI Category</div><div class="tg-val">{CATEGORY_ICONS.get(d['category'],'')} {d['category']}</div></div>
                  <div><div class="tg-lbl">Routed To</div><div class="tg-val">{d['department']}</div></div>
                </div>
                <div class="tg-lbl" style="margin-bottom:5px">Classification Confidence</div>
                {cbar(d['confidence'])}
                <hr class="div">
                <p style="font-size:.76rem;color:var(--text-soft)">Use the <strong>Track Status</strong> tab to monitor progress.</p>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("← Submit Another Complaint"):
                st.session_state.submit_result = None
                st.rerun()
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-hdr">Complaint Information</div>', unsafe_allow_html=True)
            with st.form("submit_form", clear_on_submit=False):
                c1, c2 = st.columns(2)
                with c1: name  = st.text_input("Full Name *", placeholder="e.g. Rahul Sharma")
                with c2: email = st.text_input("Email Address", placeholder="e.g. rahul@college.edu")
                desc = st.text_area(
                    "Describe the Problem *",
                    placeholder='Be specific. e.g. "Ceiling fan in Room 204, Block C has been broken for 3 days. Hostel warden not responding."',
                    height=145,
                )
                ok = st.form_submit_button("Submit Complaint →", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if ok:
                if not name.strip():
                    st.markdown('<div class="alert a-warn">⚠️ Please enter your full name.</div>', unsafe_allow_html=True)
                elif len(desc.strip()) < 10:
                    st.markdown('<div class="alert a-warn">⚠️ Please provide more detail (at least 10 characters).</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("AI is classifying your complaint..."):
                        data, code = api_post("/submit", {"student_name":name.strip(),"student_email":email.strip(),"description":desc.strip()})
                    if code == 200:
                        st.session_state.submit_result = data
                        st.rerun()
                    else:
                        st.markdown(f'<div class="alert a-err">❌ {data.get("detail","Submission failed.")}</div>', unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="card" style="margin-bottom:.9rem">
          <div class="card-hdr">How It Works</div>
          <div style="display:flex;flex-direction:column;gap:.9rem">
            <div class="step"><div class="step-num">1</div><div><div class="step-title">Submit the Complaint</div><div class="step-desc">Fill the form with a clear, specific description.</div></div></div>
            <div class="step"><div class="step-num">2</div><div><div class="step-title">AI Classification</div><div class="step-desc">LLaMA 3.1 reads and classifies your complaint automatically.</div></div></div>
            <div class="step"><div class="step-num">3</div><div><div class="step-title">Auto Routing</div><div class="step-desc">Routed instantly to the correct department executive.</div></div></div>
            <div class="step"><div class="step-num last">4</div><div><div class="step-title">Track &amp; Resolve</div><div class="step-desc">Use your Tracking ID to monitor progress in real time.</div></div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        cats = [("🚿","Bathroom & Hygiene","Housekeeping"),("🛡️","Anti-Ragging & Safety","Security Cell"),
                ("🍽️","Mess & Food Quality","Mess Committee"),("📖","Academic Issues","Academic Office"),
                ("🔧","Infrastructure","Maintenance Dept"),("📋","Other Issues","Admin Office")]
        cat_cards = "".join(f'<div class="cat-card"><div class="cat-icon">{ic}</div><div class="cat-name">{nm}</div><div class="cat-dept">→ {dp}</div></div>' for ic,nm,dp in cats)
        st.markdown(f'<div class="card"><div class="card-hdr">Categories Covered</div><div class="cat-grid">{cat_cards}</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE — TRACK
# ══════════════════════════════════════════════════════════════════════════════
elif pg == "track":
    st.markdown('<div class="page-body">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">Track Your Grievance</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Enter the Tracking ID received at the time of submission.</div>', unsafe_allow_html=True)

    c1, c2, _ = st.columns([3, 1, 2])
    with c1: tid = st.text_input("", placeholder="CPS-A1B2C3D4", label_visibility="collapsed").strip().upper()
    with c2: go  = st.button("Track →", use_container_width=True)

    if go:
        if not tid:
            st.markdown('<div class="alert a-warn">Please enter a Tracking ID.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Fetching complaint details..."):
                data, code = api_get(f"/track/{tid}")
            if code == 200:
                status = data.get("status","Submitted")
                cat    = data.get("category","Other")
                stages = ["Submitted","In Progress","Resolved"]
                si     = stages.index(status) if status in stages else 0

                tl = '<div class="timeline">'
                for i, s in enumerate(stages):
                    dc = "done" if i < si else ("current" if i == si else "")
                    sym = "✓" if i < si else str(i+1)
                    tl += f'<div style="display:flex;align-items:center"><div class="tl-dot {dc}">{sym}</div><span class="tl-lbl {dc}">{s}</span></div>'
                    if i < len(stages)-1:
                        lc = "done" if i < si else ""
                        tl += f'<div class="tl-line {lc}"></div>'
                tl += '</div>'

                st.markdown(f"""
                <div class="trk-card">
                  <div class="trk-hdr">
                    <div>
                      <div class="trk-id-lbl">Tracking ID</div>
                      <div class="trk-id-val">{data['tracking_id']}</div>
                    </div>
                    {sbadge(status)}
                  </div>
                  <div class="trk-body">
                    {tl}
                    <hr class="div">
                    <div class="trk-grid">
                      <div><div class="tg-lbl">Student</div><div class="tg-val">{data['student_name']}</div></div>
                      <div><div class="tg-lbl">Department</div><div class="tg-val">{data.get('department','—')}</div></div>
                      <div><div class="tg-lbl">Category</div><div class="tg-val">{CATEGORY_ICONS.get(cat,'')} {cat}</div></div>
                      <div><div class="tg-lbl">Submitted</div><div class="tg-val">{str(data.get('created_at',''))[:19].replace('T',' ')}</div></div>
                    </div>
                    <div class="tg-lbl" style="margin-bottom:4px">AI Confidence</div>
                    {cbar(data.get('confidence',0.75))}
                  </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**Your Complaint**")
                st.info(data.get("description",""))
                if data.get("resolution"):
                    st.markdown("**Response from Administration**")
                    st.success(data["resolution"])
                elif status == "Submitted":
                    st.markdown('<div class="alert a-info">ℹ️ Your complaint is awaiting department review.</div>', unsafe_allow_html=True)

            elif code == 404:
                st.markdown(f'<div class="alert a-err">❌ No complaint found with ID <strong>{tid}</strong>. Check the ID and try again.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert a-err">❌ Server error: {data.get("detail","")}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE — ADMIN
# ══════════════════════════════════════════════════════════════════════════════
elif pg == "admin":
    st.markdown("""
    <div class="admin-hero">
      <div class="admin-hero-inner">
        <div class="ah-eye">Restricted Access</div>
        <div class="ah-title">Admin &amp; Executive Panel</div>
        <div class="ah-sub">View, assign and resolve student complaints</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="page-body">', unsafe_allow_html=True)

    if not st.session_state.admin_auth:
        st.markdown('<div class="card" style="max-width:400px;margin:1.5rem auto">', unsafe_allow_html=True)
        st.markdown('<div class="card-hdr">Admin Login</div>', unsafe_allow_html=True)
        pwd = st.text_input("Password", type="password", placeholder="Enter admin password")
        if st.button("Login →", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.markdown('<div class="alert a-err">❌ Incorrect password.</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:.74rem;color:var(--text-soft);margin-top:.6rem">Default: <code>admin123</code></p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    lc, rc = st.columns([6,1])
    with lc: st.markdown('<div class="alert a-ok" style="display:inline-flex">✅ Logged in as Administrator</div>', unsafe_allow_html=True)
    with rc:
        if st.button("Logout"): st.session_state.admin_auth = False; st.rerun()

    st.markdown("<hr class='div'>", unsafe_allow_html=True)

    f1, f2, _, f3 = st.columns([2,2,2,1])
    with f1: fs = st.selectbox("Status",     ["All","Submitted","In Progress","Resolved","Rejected"])
    with f2: fd = st.selectbox("Department", ["All","Housekeeping Department","Security & Discipline Cell","Mess Committee","Academic Office","Maintenance Department","General Administration"])
    with f3:
        if st.button("🔄 Refresh", use_container_width=True): st.rerun()

    params = {}
    if fs != "All": params["status"]     = fs
    if fd != "All": params["department"] = fd

    data, code = api_get("/admin/problems", params=params)
    if code != 200:
        st.markdown(f'<div class="alert a-err">Failed to load: {data.get("detail","")}</div>', unsafe_allow_html=True)
        st.stop()

    problems = data.get("problems",[])
    sc = {}
    for p in problems:
        s = p.get("status","Unknown"); sc[s] = sc.get(s,0)+1

    st.markdown(f"""
    <div class="mtr-grid">
      <div class="mtr-card ml-blue"><div class="mtr-label">Total Loaded</div><div class="mtr-num">{len(problems)}</div><div class="mtr-sub">matching filters</div></div>
      <div class="mtr-card"><div class="mtr-label">🔵 Submitted</div><div class="mtr-num">{sc.get("Submitted",0)}</div><div class="mtr-sub">awaiting action</div></div>
      <div class="mtr-card ml-amber"><div class="mtr-label">🟡 In Progress</div><div class="mtr-num">{sc.get("In Progress",0)}</div><div class="mtr-sub">being actioned</div></div>
      <div class="mtr-card ml-green"><div class="mtr-label">✅ Resolved</div><div class="mtr-num">{sc.get("Resolved",0)}</div><div class="mtr-sub">closed</div></div>
    </div>
    """, unsafe_allow_html=True)

    if not problems:
        st.markdown('<div class="alert a-info">No complaints found for the selected filters.</div>', unsafe_allow_html=True)
    else:
        for p in problems:
            status = p.get("status","Submitted")
            cat    = p.get("category","Other")
            with st.expander(f"{p['tracking_id']}  ·  {p['student_name']}  ·  {CATEGORY_ICONS.get(cat,'')} {cat}  ·  {status}"):
                ci, ca = st.columns([3,2])
                with ci:
                    st.markdown(f"""
                    <div style="margin-bottom:.65rem">
                      <span class="tg-lbl">Tracking ID</span><br>
                      <span style="font-family:'JetBrains Mono',monospace;font-size:.88rem;color:var(--navy);font-weight:600">{p['tracking_id']}</span>
                    </div>
                    <div style="font-size:.76rem;color:var(--text-soft);margin-bottom:3px"><b>Student:</b> {p['student_name']} {'('+p['student_email']+')' if p.get('student_email') else ''}</div>
                    <div style="font-size:.76rem;color:var(--text-soft);margin-bottom:3px"><b>Department:</b> {p.get('department','—')}</div>
                    <div style="font-size:.76rem;color:var(--text-soft);margin-bottom:.65rem"><b>Submitted:</b> {str(p.get('created_at',''))[:19].replace('T',' ')}</div>
                    <div class="tg-lbl" style="margin-bottom:4px">AI Confidence</div>
                    {cbar(p.get('confidence',0.75))}
                    """, unsafe_allow_html=True)
                    if p.get("reason"):
                        st.markdown(f'<div style="font-size:.71rem;color:var(--text-soft);margin-top:3px">AI reason: {p["reason"]}</div>', unsafe_allow_html=True)
                    st.markdown("<br>**Description**", unsafe_allow_html=True)
                    st.info(p.get("description",""))
                    if p.get("resolution"):
                        st.success(f"**Resolution:** {p['resolution']}")
                with ca:
                    st.markdown('<div class="card"><div class="card-hdr">Update Status</div>', unsafe_allow_html=True)
                    idx = ["Submitted","In Progress","Resolved","Rejected"]
                    ns  = st.selectbox("Status", idx, index=idx.index(status) if status in idx else 0, key=f"ns_{p['id']}")
                    rt  = st.text_area("Resolution / Comment", value=p.get("resolution",""), height=90, key=f"rt_{p['id']}", placeholder="Describe action taken...")
                    if st.button("💾 Save Update", key=f"sv_{p['id']}", use_container_width=True):
                        resp, rc2 = api_put(f"/admin/problem/{p['id']}", {"status":ns,"resolution":rt})
                        if rc2 == 200: st.success("Updated!"); st.rerun()
                        else: st.error(resp.get("detail","Failed"))
                    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE — STATS
# ══════════════════════════════════════════════════════════════════════════════
elif pg == "stats":
    st.markdown("""
    <div class="admin-hero">
      <div class="admin-hero-inner">
        <div class="ah-eye">Live Data</div>
        <div class="ah-title">Grievance Statistics</div>
        <div class="ah-sub">Campus-wide complaint analytics</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="page-body">', unsafe_allow_html=True)
    data, code = api_get("/admin/stats")
    if code != 200:
        st.markdown('<div class="alert a-err">Could not load statistics.</div>', unsafe_allow_html=True)
        st.stop()

    total       = data.get("total",0)
    by_status   = data.get("by_status",{})
    by_category = data.get("by_category",{})
    by_dept     = data.get("by_department",{})
    resolved    = by_status.get("Resolved",0)
    rr          = f"{int(resolved/total*100)}%" if total else "—"

    st.markdown(f"""
    <div class="mtr-grid">
      <div class="mtr-card ml-blue"><div class="mtr-label">Total Complaints</div><div class="mtr-num">{total}</div><div class="mtr-sub">all time</div></div>
      <div class="mtr-card ml-green"><div class="mtr-label">Resolved</div><div class="mtr-num">{resolved}</div><div class="mtr-sub">rate: {rr}</div></div>
      <div class="mtr-card ml-amber"><div class="mtr-label">In Progress</div><div class="mtr-num">{by_status.get("In Progress",0)}</div><div class="mtr-sub">being actioned</div></div>
      <div class="mtr-card"><div class="mtr-label">Pending</div><div class="mtr-num">{by_status.get("Submitted",0)}</div><div class="mtr-sub">awaiting action</div></div>
    </div>
    """, unsafe_allow_html=True)

    l, r = st.columns(2, gap="large")
    with l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-hdr">By Category</div>', unsafe_allow_html=True)
        for cat, cnt in sorted(by_category.items(), key=lambda x: -x[1]):
            pct = int(cnt/total*100) if total else 0
            ic  = CATEGORY_ICONS.get(cat,"📋")
            st.markdown(f"""
            <div class="bar-row">
              <div class="bar-top"><span class="bar-name">{ic} {cat}</span><span class="bar-cnt">{cnt} · {pct}%</span></div>
              <div class="bar-bg"><div class="bar-fill" style="width:{pct}%;background:var(--navy)"></div></div>
            </div>""", unsafe_allow_html=True)
        if not by_category:
            st.markdown('<div class="alert a-info">No data yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-hdr">By Department</div>', unsafe_allow_html=True)
        for dept, cnt in sorted(by_dept.items(), key=lambda x: -x[1]):
            pct = int(cnt/total*100) if total else 0
            st.markdown(f"""
            <div class="bar-row">
              <div class="bar-top"><span class="bar-name">🏢 {dept}</span><span class="bar-cnt">{cnt} · {pct}%</span></div>
              <div class="bar-bg"><div class="bar-fill" style="width:{pct}%;background:var(--amber)"></div></div>
            </div>""", unsafe_allow_html=True)
        if not by_dept:
            st.markdown('<div class="alert a-info">No data yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    status_colors_map = {"Submitted":"#2563EB","In Progress":"#D97706","Resolved":"#059669","Rejected":"#DC2626"}
    sb_html = '<div class="card" style="margin-top:1rem"><div class="card-hdr">Status Breakdown</div><div class="sb-grid">'
    for s in ["Submitted","In Progress","Resolved","Rejected"]:
        cnt = by_status.get(s,0); pct = int(cnt/total*100) if total else 0
        c = status_colors_map[s]
        sb_html += f'<div class="sb-card"><div class="sb-num" style="color:{c}">{cnt}</div><div class="sb-lbl">{s}</div><div class="sb-pct">{pct}% of total</div></div>'
    sb_html += '</div></div>'
    st.markdown(sb_html, unsafe_allow_html=True)

    if st.button("🔄 Refresh Statistics"): st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="portal-footer">
  <span>CampusGriev</span> · Student Grievance Management System ·
  Powered by <span>LLaMA 3.1</span> via Groq ·
  <span>All complaints are confidential</span>
</div>
""", unsafe_allow_html=True)