import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL    = os.getenv("BACKEND_URL", "http://localhost:8000")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

CATEGORY_ICONS = {
    "Bathroom & Hygiene":         "🚿",
    "Anti-Ragging & Safety":      "🛡️",
    "Mess & Food Quality":        "🍽️",
    "Academic Issues":            "📖",
    "Infrastructure/Maintenance": "🔧",
    "Other":                      "📋",
}

AUTHORITY_ICONS = {
    "Department":  "🏢",
    "Warden":      "👨‍💼",
    "Head Warden": "👔",
    "Director":    "🎓",
}

PRIORITY_META = {
    "critical": {"label":"CRITICAL","color":"#DC2626","bg":"#FEF2F2","border":"#FCA5A5","icon":"🚨"},
    "high":     {"label":"HIGH",    "color":"#D97706","bg":"#FFFBEB","border":"#FCD34D","icon":"⚠️"},
    "normal":   {"label":"NORMAL",  "color":"#059669","bg":"#F0FDF4","border":"#86EFAC","icon":"✅"},
}

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CampusGriev — Student Grievance Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
#  CSS — injected via JS so Streamlit Cloud cannot strip the <style> tag
# ══════════════════════════════════════════════════════════════════════════════
import streamlit.components.v1 as _components

_components.html("""
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --navy:#0B1E3F;--navy-light:#1e3a6e;
  --amber:#D97706;--amber-lt:#FEF3C7;
  --green:#059669;--green-lt:#D1FAE5;
  --red:#DC2626;--red-lt:#FEE2E2;
  --blue:#2563EB;--blue-lt:#DBEAFE;
  --border:#E2E8F0;--white:#FFFFFF;
  --text:#0F172A;--text-mid:#334155;--text-soft:#64748B;
  --slate-lt:#F1F5F9;--radius:10px;
  --shadow:0 1px 3px rgba(0,0,0,.08),0 4px 16px rgba(0,0,0,.04);
  --shadow-md:0 4px 12px rgba(0,0,0,.10),0 12px 32px rgba(0,0,0,.06);
}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main{
  font-family:'DM Sans',sans-serif!important;background:#F8FAFC!important;color:var(--text)!important;
}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebarNav"],button[title="View fullscreen"],.stDeployButton{display:none!important}
[data-testid="stSidebar"]{display:none!important}
.block-container{padding:0!important;max-width:100%!important}

/* NAV */
.topnav{background:var(--navy);padding:0 2.5rem;display:flex;align-items:center;
  justify-content:space-between;height:64px;border-bottom:3px solid var(--amber);
  box-shadow:0 2px 20px rgba(0,0,0,.25)}
.topnav-brand{display:flex;align-items:center;gap:12px}
.topnav-logo{width:38px;height:38px;background:var(--amber);border-radius:8px;
  display:flex;align-items:center;justify-content:center;font-size:1.1rem;
  font-weight:700;color:var(--navy);font-family:'DM Serif Display',serif}
.topnav-name{font-family:'DM Serif Display',serif;font-size:1.2rem;color:white}
.topnav-sub{font-size:.63rem;color:#94A3B8;letter-spacing:.08em;text-transform:uppercase}
.status-pill{display:flex;align-items:center;gap:6px;font-size:.73rem;color:#94A3B8}
.sdot{width:7px;height:7px;border-radius:50%;background:#10B981;animation:blink 2s infinite}
.sdot.off{background:#EF4444;animation:none}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.5}}

/* TABS */
.page-tabs{background:white;border-bottom:1px solid var(--border);padding:0 2.5rem;display:flex}
.ptab{padding:.85rem 1.3rem;font-size:.81rem;font-weight:600;color:var(--text-soft);
  border-bottom:3px solid transparent;font-family:'DM Sans',sans-serif;background:none;
  border-top:none;border-left:none;border-right:none;cursor:pointer;white-space:nowrap;transition:all .15s}
.ptab:hover{color:var(--navy);background:var(--slate-lt)}
.ptab.active{color:var(--navy);border-bottom-color:var(--amber)}

/* HERO */
.hero{background:linear-gradient(135deg,var(--navy) 0%,var(--navy-light) 100%);
  padding:2.8rem 2.5rem;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:-60px;right:-60px;width:280px;height:280px;
  background:var(--amber);opacity:.06;border-radius:50%}
.hero-inner{max-width:1100px;margin:0 auto;position:relative;z-index:1}
.hero-eyebrow{font-size:.68rem;text-transform:uppercase;letter-spacing:.15em;color:var(--amber);font-weight:600;margin-bottom:.6rem}
.hero h1{font-family:'DM Serif Display',serif;font-size:2rem;color:white;line-height:1.15;margin-bottom:.5rem}
.hero p{font-size:.9rem;color:#94A3B8;max-width:500px;line-height:1.6;margin-bottom:1.25rem}
.hero-stats{display:flex;gap:2rem}
.hs-num{font-family:'DM Serif Display',serif;font-size:1.4rem;color:var(--amber)}
.hs-label{font-size:.68rem;color:#94A3B8;text-transform:uppercase;letter-spacing:.06em}

/* admin/stats banner */
.admin-hero{background:var(--navy);padding:1.4rem 2.5rem;border-bottom:3px solid var(--amber)}
.admin-hero-inner{max-width:1100px;margin:0 auto}
.ah-eye{font-size:.63rem;letter-spacing:.12em;color:var(--amber);text-transform:uppercase;font-weight:700;margin-bottom:3px}
.ah-title{font-family:'DM Serif Display',serif;font-size:1.5rem;color:white}
.ah-sub{font-size:.8rem;color:#64748B;margin-top:3px}

/* BODY */
.page-body{max-width:1100px;margin:0 auto;padding:1.8rem 2.5rem 4rem}

/* CARDS */
.card{background:white;border:1px solid var(--border);border-radius:var(--radius);padding:1.4rem;box-shadow:var(--shadow)}
.card-hdr{font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;font-weight:700;color:var(--text-soft);
  margin-bottom:.9rem;padding-bottom:.7rem;border-bottom:1px solid var(--border)}

/* METRICS */
.mtr-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.4rem}
.mtr-card{background:white;border:1px solid var(--border);border-radius:var(--radius);padding:1.1rem 1.3rem;box-shadow:var(--shadow)}
.mtr-label{font-size:.67rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-soft);font-weight:600;margin-bottom:.35rem}
.mtr-num{font-family:'DM Serif Display',serif;font-size:1.9rem;color:var(--navy);line-height:1}
.mtr-sub{font-size:.7rem;color:var(--text-soft);margin-top:3px}
.ml-amber{border-left:3px solid var(--amber)}.ml-green{border-left:3px solid var(--green)}
.ml-blue{border-left:3px solid var(--blue)}.ml-red{border-left:3px solid var(--red)}

/* BADGES */
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:99px;
  font-size:.71rem;font-weight:700;letter-spacing:.03em}
.b-sub{background:#DBEAFE;color:#1D4ED8}.b-prg{background:#FEF3C7;color:#92400E}
.b-res{background:#D1FAE5;color:#065F46}.b-rej{background:#FEE2E2;color:#991B1B}
.b-esc{background:#EDE9FE;color:#5B21B6}

/* PRIORITY BANNER */
.priority-banner{padding:.7rem 1rem;border-radius:8px;font-size:.82rem;font-weight:600;
  display:flex;align-items:center;gap:8px;margin-bottom:.9rem;border:1px solid}

/* ESCALATION LADDER */
.esc-ladder{display:flex;gap:0;margin:1rem 0}
.esc-step{display:flex;align-items:center}
.esc-node{padding:.35rem .8rem;border-radius:99px;font-size:.72rem;font-weight:700;
  background:var(--slate-lt);border:1.5px solid var(--border);color:var(--text-soft);white-space:nowrap}
.esc-node.done{background:#EDE9FE;border-color:#8B5CF6;color:#5B21B6}
.esc-node.current{background:var(--navy);border-color:var(--navy);color:white}
.esc-arrow{font-size:.9rem;margin:0 4px;color:var(--border)}
.esc-arrow.done{color:#8B5CF6}

/* TRACKING CARD */
.trk-card{background:white;border:1px solid var(--border);border-radius:var(--radius);
  overflow:hidden;box-shadow:var(--shadow-md)}
.trk-hdr{background:var(--navy);padding:1.2rem 1.4rem;display:flex;align-items:center;justify-content:space-between}
.trk-id-lbl{font-size:.63rem;color:#64748B;text-transform:uppercase;letter-spacing:.1em}
.trk-id-val{font-family:'JetBrains Mono',monospace;font-size:1.2rem;color:var(--amber);font-weight:600}
.trk-body{padding:1.4rem}
.trk-grid{display:grid;grid-template-columns:1fr 1fr;gap:.9rem;margin-bottom:1.1rem}
.tg-lbl{font-size:.68rem;text-transform:uppercase;letter-spacing:.07em;color:var(--text-soft);font-weight:600;margin-bottom:2px}
.tg-val{font-size:.88rem;color:var(--text);font-weight:500}

/* DISPUTE BOX */
.dispute-box{background:#FFF7ED;border:1.5px solid #FED7AA;border-radius:8px;padding:1rem 1.1rem;margin-top:1rem}
.dispute-title{font-weight:700;color:#7C2D12;font-size:.85rem;margin-bottom:.4rem}
.dispute-sub{font-size:.78rem;color:#9A3412;line-height:1.5}

/* ALERTS */
.alert{padding:.8rem 1rem;border-radius:8px;font-size:.83rem;margin:.6rem 0;
  display:flex;gap:9px;align-items:flex-start;line-height:1.5}
.a-ok{background:#D1FAE5;color:#065F46;border:1px solid #6EE7B7}
.a-err{background:#FEE2E2;color:#7F1D1D;border:1px solid #FCA5A5}
.a-info{background:#DBEAFE;color:#1E3A8A;border:1px solid #93C5FD}
.a-warn{background:#FEF3C7;color:#78350F;border:1px solid #FCD34D}
.a-purple{background:#EDE9FE;color:#4C1D95;border:1px solid #C4B5FD}

/* CONF BAR */
.conf-wrap{display:flex;align-items:center;gap:8px}
.conf-bg{flex:1;height:5px;background:var(--slate-lt);border-radius:99px;overflow:hidden}
.conf-fill{height:100%;border-radius:99px}
.conf-pct{font-size:.7rem;font-weight:600;color:var(--text-soft);min-width:26px}

/* STEPS (how it works) */
.step{display:flex;gap:11px;align-items:flex-start}
.step-num{width:24px;height:24px;border-radius:50%;background:var(--navy);color:white;
  display:flex;align-items:center;justify-content:center;font-size:.68rem;font-weight:700;flex-shrink:0}
.step-num.amber{background:var(--amber)}
.step-title{font-weight:600;font-size:.83rem;color:var(--navy)}
.step-desc{font-size:.76rem;color:var(--text-soft);margin-top:1px}

/* CAT GRID */
.cat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.65rem;margin-top:.9rem}
.cat-card{background:var(--slate-lt);border:1px solid var(--border);border-radius:8px;padding:.75rem}
.cat-icon{font-size:1rem;margin-bottom:3px}
.cat-name{font-weight:600;font-size:.76rem;color:var(--navy)}
.cat-dept{font-size:.68rem;color:var(--text-soft);margin-top:1px}

/* BAR ROWS */
.bar-row{margin-bottom:.85rem}
.bar-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:3px}
.bar-name{font-size:.81rem;font-weight:600;color:var(--text)}
.bar-cnt{font-size:.76rem;color:var(--text-soft)}
.bar-bg{background:var(--slate-lt);border-radius:99px;height:6px}
.bar-fill{height:6px;border-radius:99px}

/* STATUS BLOCKS */
.sb-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.9rem}
.sb-card{text-align:center;padding:.9rem;background:var(--slate-lt);border-radius:8px;border:1px solid var(--border)}
.sb-num{font-family:'DM Serif Display',serif;font-size:1.7rem;line-height:1}
.sb-lbl{font-size:.73rem;font-weight:600;color:var(--text-mid);margin:2px 0}
.sb-pct{font-size:.68rem;color:var(--text-soft)}

.div{border:none;border-top:1px solid var(--border);margin:1.25rem 0}

/* STREAMLIT OVERRIDES */
[data-testid="stTextInput"] label,[data-testid="stTextArea"] label,[data-testid="stSelectbox"] label{
  font-size:.76rem!important;font-weight:600!important;color:var(--text-mid)!important;
  text-transform:uppercase!important;letter-spacing:.06em!important;font-family:'DM Sans',sans-serif!important}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{
  border:1.5px solid var(--border)!important;border-radius:8px!important;
  font-family:'DM Sans',sans-serif!important;font-size:.89rem!important;color:var(--text)!important;background:white!important}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{
  border-color:var(--navy)!important;box-shadow:0 0 0 3px rgba(11,30,63,.08)!important;outline:none!important}
[data-testid="stFormSubmitButton"] button,.stButton > button{
  background:var(--navy)!important;color:white!important;border:none!important;border-radius:8px!important;
  font-family:'DM Sans',sans-serif!important;font-weight:600!important;font-size:.84rem!important;
  transition:all .15s!important;box-shadow:0 2px 6px rgba(11,30,63,.22)!important}
[data-testid="stFormSubmitButton"] button:hover,.stButton > button:hover{
  background:var(--navy-light)!important;transform:translateY(-1px)!important}
[data-testid="stSelectbox"] > div > div{
  border:1.5px solid var(--border)!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important}
[data-testid="stExpander"]{
  border:1px solid var(--border)!important;border-radius:var(--radius)!important;
  box-shadow:var(--shadow)!important;background:white!important;margin-bottom:.5rem!important}
[data-testid="stExpander"] summary{
  font-family:'DM Sans',sans-serif!important;font-weight:600!important;
  font-size:.83rem!important;color:var(--text)!important;padding:.8rem 1rem!important}
.stForm{border:none!important;padding:0!important;background:none!important}
[data-testid="stVerticalBlock"] > div{margin-bottom:0!important}

/* FOOTER */
.portal-footer{background:var(--navy);color:#475569;text-align:center;
  padding:1.4rem;font-size:.73rem;margin-top:3rem;letter-spacing:.02em}
.portal-footer span{color:#94A3B8}

/* ── TAB BUTTONS ─────────────────────────────────────── */
/* Style ALL buttons that are direct children of the first horizontal block */
section.main > div > div > div > div > div[data-testid="stHorizontalBlock"] .stButton > button,
div[data-testid="stHorizontalBlock"] .stButton > button {
  background: white !important;
  color: #64748B !important;
  border: none !important;
  border-bottom: 3px solid transparent !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  padding: .8rem .4rem !important;
  font-size: .78rem !important;
  font-weight: 600 !important;
  width: 100% !important;
  transition: color .15s, border-color .15s !important;
  font-family: 'DM Sans', sans-serif !important;
  margin: 0 !important;
}
section.main > div > div > div > div > div[data-testid="stHorizontalBlock"] .stButton > button:hover,
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
  color: #0B1E3F !important;
  background: #F8FAFC !important;
}
/* Tab row container */
div[data-testid="stHorizontalBlock"] {
  background: white !important;
  border-bottom: 1px solid #E2E8F0 !important;
  gap: 0 !important;
  padding: 0 1rem !important;
  margin-bottom: 0 !important;
}
</style>
<script>
(function() {
  var doc = window.parent.document;

  // 1. Inject Google Fonts
  if (!doc.getElementById('cg-fonts')) {
    var link = doc.createElement('link');
    link.id = 'cg-fonts';
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap';
    doc.head.appendChild(link);
  }

  // 2. Inject CSS into parent
  var style = document.querySelector('style');
  if (style) {
    var existing = doc.getElementById('cg-styles');
    if (existing) existing.remove();
    var ps = doc.createElement('style');
    ps.id = 'cg-styles';
    ps.textContent = style.textContent;
    doc.head.appendChild(ps);
  }
})();
</script>
""", height=0)

# ══════════════════════════════════════════════════════════════════════════════
#  STATE & HELPERS
# ══════════════════════════════════════════════════════════════════════════════
if "page"          not in st.session_state: st.session_state.page          = "submit"
if "admin_auth"    not in st.session_state: st.session_state.admin_auth    = False
if "submit_result" not in st.session_state: st.session_state.submit_result = None

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
    cls = {"Submitted":"b-sub","In Progress":"b-prg","Resolved":"b-res",
           "Rejected":"b-rej","Escalated":"b-esc"}.get(status,"b-sub")
    dot = {"Submitted":"●","In Progress":"◐","Resolved":"✓","Rejected":"✕","Escalated":"↑"}.get(status,"●")
    return f'<span class="badge {cls}">{dot} {status}</span>'

def cbar(score):
    p = int(score * 100)
    c = "#059669" if p >= 75 else "#D97706" if p >= 50 else "#DC2626"
    return f'<div class="conf-wrap"><div class="conf-bg"><div class="conf-fill" style="width:{p}%;background:{c}"></div></div><span class="conf-pct">{p}%</span></div>'

def priority_banner(priority, is_medical=False, is_repeat=False):
    m = PRIORITY_META.get(priority, PRIORITY_META["normal"])
    extra = []
    if is_medical: extra.append("🏥 Medical issue detected")
    if is_repeat:  extra.append("🔁 Repeat complaint")
    extra_html = " &nbsp;·&nbsp; ".join(extra) if extra else ""
    return f"""
    <div class="priority-banner" style="background:{m['bg']};border-color:{m['border']};color:{m['color']}">
      {m['icon']} Priority: <strong>{m['label']}</strong>
      {f"&nbsp;&nbsp;<span style='font-weight:400;font-size:.78rem'>{extra_html}</span>" if extra_html else ""}
    </div>"""

def escalation_ladder_html(current_level):
    steps  = [("Department",0),("Warden",1),("Head Warden",2),("Director",3)]
    icons  = {0:"🏢",1:"👨‍💼",2:"👔",3:"🎓"}
    html   = '<div class="esc-ladder">'
    for name, lvl in steps:
        if lvl < current_level:
            cls = "esc-node done"
        elif lvl == current_level:
            cls = "esc-node current"
        else:
            cls = "esc-node"
        html += f'<div class="esc-step"><div class="{cls}">{icons[lvl]} {name}</div></div>'
        if lvl < 3:
            arrow_cls = "esc-arrow done" if lvl < current_level else "esc-arrow"
            html += f'<span class="{arrow_cls}">›</span>'
    html += '</div>'
    return html

# ── Backend check & hero stats ────────────────────────────────────────────────
backend_ok = False
try:
    _, _c = api_get("/"); backend_ok = (_c == 200)
except: pass

hero_total = hero_res = hero_pend = 0
try:
    sd, sc = api_get("/admin/stats")
    if sc == 200:
        hero_total = sd.get("total", 0)
        hero_res   = sd.get("by_status",{}).get("Resolved", 0)
        hero_pend  = sd.get("by_status",{}).get("Submitted",0) + sd.get("by_status",{}).get("In Progress",0)
except: pass

# ══════════════════════════════════════════════════════════════════════════════
#  NAVBAR
# ══════════════════════════════════════════════════════════════════════════════
dot     = "sdot" if backend_ok else "sdot off"
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
  <div class="status-pill"><div class="{dot}"></div><span>{dot_txt}</span></div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB BAR
# ══════════════════════════════════════════════════════════════════════════════
tabs_def = [
    ("submit",    "📝  Submit Grievance"),
    ("track",     "🔍  Track Status"),
    ("escalation","⚡  Escalation Queue"),
    ("admin",     "🛠  Admin Panel"),
    ("stats",     "📊  Statistics"),
]
pg = st.session_state.page

# ── Tab bar: plain st.button() calls — all styling via JS-injected CSS ───────
active_idx = [k for k, _ in tabs_def].index(pg)
tab_cols = st.columns(len(tabs_def))
for i, (k, lbl) in enumerate(tabs_def):
    with tab_cols[i]:
        if st.button(lbl, key=f"tb_{k}", use_container_width=True):
            st.session_state.page = k
            st.rerun()

# Highlight active tab with amber underline via JS (no <style> tag needed)
_components.html(f"""
<script>
(function() {{
  var doc = window.parent.document;
  var activeIdx = {active_idx};
  // Run after Streamlit has rendered the buttons
  setTimeout(function() {{
    var hblock = doc.querySelector('div[data-testid="stHorizontalBlock"]');
    if (!hblock) return;
    var btns = hblock.querySelectorAll('button');
    btns.forEach(function(btn, i) {{
      btn.style.borderBottom = '3px solid transparent';
      btn.style.color = '#64748B';
    }});
    if (btns[activeIdx]) {{
      btns[activeIdx].style.borderBottom = '3px solid #D97706';
      btns[activeIdx].style.color = '#0B1E3F';
    }}
  }}, 100);
}})();
</script>
""", height=0)

# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
if pg in ("submit","track"):
    hero_map = {
        "submit":("RAISE A COMPLAINT","Submit Your Grievance",
                  "Describe your problem. Our AI classifies and routes it instantly — medical issues jump the queue automatically."),
        "track": ("TRACK YOUR COMPLAINT","Check Grievance Status",
                  "Enter your Tracking ID. If your issue was marked resolved but isn't — you can dispute it and escalate."),
    }
    ey,h1,p = hero_map[pg]
    st.markdown(f"""
    <div class="hero">
      <div class="hero-inner">
        <div class="hero-eyebrow">{ey}</div>
        <h1>{h1}</h1><p>{p}</p>
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
            d      = st.session_state.submit_result
            p_meta = PRIORITY_META.get(d.get("priority","normal"), PRIORITY_META["normal"])
            lv     = d.get("escalation_level", 0)

            st.markdown(f"""
            <div class="trk-card" style="margin-bottom:1.2rem">
              <div class="trk-hdr">
                <div>
                  <div class="trk-id-lbl">Your Tracking ID — save this</div>
                  <div class="trk-id-val">{d['tracking_id']}</div>
                </div>
                {sbadge(d.get('status','Submitted'))}
              </div>
              <div class="trk-body">
                {priority_banner(d.get('priority','normal'), d.get('is_medical',False), d.get('is_repeat',False))}
                <div class="alert a-ok" style="margin-bottom:.9rem">
                  ✅ Complaint submitted and routed to <strong>{d['department']}</strong>.
                  {' &nbsp;🏥 <strong>Escalated to Warden due to medical nature.</strong>' if d.get('is_medical') else ''}
                </div>
                <div class="trk-grid">
                  <div><div class="tg-lbl">AI Category</div><div class="tg-val">{CATEGORY_ICONS.get(d['category'],'')} {d['category']}</div></div>
                  <div><div class="tg-lbl">Current Authority</div><div class="tg-val">{AUTHORITY_ICONS.get(d['current_authority'],'')} {d['current_authority']}</div></div>
                </div>
                <div class="tg-lbl" style="margin-bottom:5px">Escalation Level</div>
                {escalation_ladder_html(lv)}
                <div class="tg-lbl" style="margin-bottom:5px;margin-top:.75rem">Classification Confidence</div>
                {cbar(d['confidence'])}
                <hr class="div">
                <p style="font-size:.76rem;color:var(--text-soft)">Use the <strong>Track Status</strong> tab to monitor progress. If marked resolved but not fixed — you can dispute it.</p>
              </div>
            </div>""", unsafe_allow_html=True)

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
                    placeholder='Be specific. e.g. "I have a severe fever of 104°F and the hostel warden is not responding. Need medical help."',
                    height=145,
                )
                ok = st.form_submit_button("Submit Complaint →", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="alert a-info" style="margin-top:.7rem">
              ℹ️ <strong>Medical issues</strong> (fever, injury, emergency) are automatically flagged 🚨 <strong>CRITICAL</strong>
              and escalated directly to the Warden — no waiting.
            </div>""", unsafe_allow_html=True)

            if ok:
                if not name.strip():
                    st.markdown('<div class="alert a-warn">⚠️ Please enter your full name.</div>', unsafe_allow_html=True)
                elif len(desc.strip()) < 10:
                    st.markdown('<div class="alert a-warn">⚠️ Please provide more detail.</div>', unsafe_allow_html=True)
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
            <div class="step"><div class="step-num">1</div><div><div class="step-title">Submit</div><div class="step-desc">Describe the problem clearly.</div></div></div>
            <div class="step"><div class="step-num">2</div><div><div class="step-title">AI Classification</div><div class="step-desc">LLaMA 3.1 classifies, detects medical urgency and repeat patterns.</div></div></div>
            <div class="step"><div class="step-num">3</div><div><div class="step-title">Auto Routing & Priority</div><div class="step-desc">Routed to department. Medical/repeat issues get higher priority.</div></div></div>
            <div class="step"><div class="step-num amber">4</div><div><div class="step-title">Dispute if Needed</div><div class="step-desc">If marked resolved but not fixed — dispute it. Escalates automatically to Warden → Head Warden → Director.</div></div></div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
          <div class="card-hdr">Escalation Hierarchy</div>
          <div style="display:flex;flex-direction:column;gap:.6rem;margin-top:.3rem">
            <div style="display:flex;gap:10px;align-items:center">
              <span style="font-size:1.1rem">🏢</span>
              <div><div style="font-weight:600;font-size:.8rem;color:var(--navy)">Department</div>
              <div style="font-size:.72rem;color:var(--text-soft)">First point of contact</div></div>
            </div>
            <div style="display:flex;gap:10px;align-items:center">
              <span style="font-size:1.1rem">👨‍💼</span>
              <div><div style="font-weight:600;font-size:.8rem;color:var(--navy)">Warden</div>
              <div style="font-size:.72rem;color:var(--text-soft)">Dispute #1 or medical issue</div></div>
            </div>
            <div style="display:flex;gap:10px;align-items:center">
              <span style="font-size:1.1rem">👔</span>
              <div><div style="font-weight:600;font-size:.8rem;color:var(--navy)">Head Warden</div>
              <div style="font-size:.72rem;color:var(--text-soft)">Dispute #3 or unresolved escalation</div></div>
            </div>
            <div style="display:flex;gap:10px;align-items:center">
              <span style="font-size:1.1rem">🎓</span>
              <div><div style="font-weight:600;font-size:.8rem;color:var(--navy)">Director</div>
              <div style="font-size:.72rem;color:var(--text-soft)">Dispute #5 or final escalation</div></div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE — TRACK
# ══════════════════════════════════════════════════════════════════════════════
elif pg == "track":
    st.markdown('<div class="page-body">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title" style="font-family:\'DM Serif Display\',serif;font-size:1.35rem;color:var(--navy)">Track Your Grievance</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.8rem;color:var(--text-soft);margin-bottom:1rem">Enter the Tracking ID received at submission. You can dispute a resolution if your issue is still unresolved.</div>', unsafe_allow_html=True)

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
                status   = data.get("status","Submitted")
                cat      = data.get("category","Other")
                lv       = data.get("escalation_level", 0)
                priority = data.get("priority","normal")
                disputes = data.get("dispute_count", 0)

                # Build status timeline
                if status in ["Escalated"]:
                    stages = ["Submitted","Escalated","In Progress","Resolved"]
                else:
                    stages = ["Submitted","In Progress","Resolved"]
                si    = stages.index(status) if status in stages else 0
                tl    = '<div style="display:flex;align-items:center;margin:1rem 0">'
                for i, s in enumerate(stages):
                    dc = "done" if i < si else ("current" if i == si else "")
                    sym = "✓" if i < si else str(i+1)
                    tl += f'<div style="display:flex;align-items:center"><div class="esc-node {dc}" style="width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.68rem;font-weight:700;padding:0">{sym}</div><span style="font-size:.69rem;font-weight:600;margin-left:5px;color:{"var(--navy)" if dc=="done" else "var(--amber)" if dc=="current" else "var(--text-soft)"};white-space:nowrap">{s}</span></div>'
                    if i < len(stages)-1:
                        lc = "done" if i < si else ""
                        tl += f'<div style="flex:1;height:2px;background:{"var(--navy)" if lc=="done" else "var(--border)"};min-width:18px"></div>'
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
                    {priority_banner(priority, data.get('is_medical',False), data.get('is_repeat',False))}
                    {tl}
                    <div style="margin:1rem 0">
                      <div class="tg-lbl" style="margin-bottom:5px">Current Authority</div>
                      {escalation_ladder_html(lv)}
                    </div>
                    <hr class="div">
                    <div class="trk-grid">
                      <div><div class="tg-lbl">Student</div><div class="tg-val">{data['student_name']}</div></div>
                      <div><div class="tg-lbl">Department</div><div class="tg-val">{data.get('department','—')}</div></div>
                      <div><div class="tg-lbl">Category</div><div class="tg-val">{CATEGORY_ICONS.get(cat,'')} {cat}</div></div>
                      <div><div class="tg-lbl">Submitted</div><div class="tg-val">{str(data.get('created_at',''))[:19].replace('T',' ')}</div></div>
                    </div>
                    {f'<div class="alert a-purple" style="margin-top:.5rem">↑ Escalation reason: <strong>{data["escalation_reason"]}</strong> &nbsp;·&nbsp; Disputes filed: <strong>{disputes}</strong></div>' if lv > 0 else ''}
                  </div>
                </div>""", unsafe_allow_html=True)

                st.markdown("**Your Complaint**")
                st.info(data.get("description",""))

                if data.get("resolution"):
                    st.markdown("**Response from Administration**")
                    st.success(data["resolution"])

                # ── DISPUTE BUTTON ─────────────────────────────────────
                if status in ("Resolved", "Rejected"):
                    st.markdown("""
                    <div class="dispute-box">
                      <div class="dispute-title">⚠️ Is your issue still unresolved?</div>
                      <div class="dispute-sub">If this complaint was marked resolved but the problem persists,
                      you can dispute it. It will be automatically escalated to a higher authority.</div>
                    </div>""", unsafe_allow_html=True)

                    next_auth = {0:"Warden",1:"Warden",2:"Head Warden",3:"Director (final)"}.get(lv,"Warden")
                    st.markdown(f"<div style='font-size:.78rem;color:var(--text-soft);margin:.5rem 0'>This will escalate your complaint to: <strong>{next_auth}</strong></div>", unsafe_allow_html=True)

                    dispute_reason = st.text_area(
                        "Why is it not resolved? (optional)",
                        placeholder="e.g. The plumber came but the issue is still there...",
                        height=80,
                        key="dispute_reason",
                    )

                    if lv >= 3:
                        st.markdown('<div class="alert a-warn">⚠️ This complaint is already at Director level — the highest authority. Please contact the administration directly.</div>', unsafe_allow_html=True)
                    else:
                        if st.button(f"🔺 Dispute & Escalate to {next_auth}", use_container_width=False):
                            with st.spinner("Filing dispute..."):
                                resp, rc = api_post(f"/dispute/{tid}", {
                                    "reason": dispute_reason or "Student reports issue is not resolved"
                                })
                            if rc == 200:
                                st.markdown(f"""
                                <div class="alert a-purple">
                                  ↑ <strong>Dispute filed successfully.</strong>
                                  Your complaint has been escalated to <strong>{resp['current_authority']}</strong>.
                                  Dispute #{resp['dispute_count']} on record.
                                </div>""", unsafe_allow_html=True)
                                st.rerun()
                            else:
                                st.markdown(f'<div class="alert a-err">❌ {resp.get("detail","Failed to file dispute.")}</div>', unsafe_allow_html=True)

                elif status == "Submitted":
                    st.markdown('<div class="alert a-info" style="margin-top:.7rem">ℹ️ Your complaint is awaiting department review.</div>', unsafe_allow_html=True)
                elif status == "Escalated":
                    auth = data.get("current_authority","higher authority")
                    st.markdown(f'<div class="alert a-purple" style="margin-top:.7rem">↑ Your complaint is under review by the <strong>{auth}</strong>.</div>', unsafe_allow_html=True)

            elif code == 404:
                st.markdown(f'<div class="alert a-err">❌ No complaint found with ID <strong>{tid}</strong>.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert a-err">❌ Server error: {data.get("detail","")}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE — ESCALATION QUEUE
# ══════════════════════════════════════════════════════════════════════════════
elif pg == "escalation":
    st.markdown("""
    <div class="admin-hero">
      <div class="admin-hero-inner">
        <div class="ah-eye">Priority View</div>
        <div class="ah-title">⚡ Escalation Queue</div>
        <div class="ah-sub">Critical & escalated complaints sorted by urgency — medical issues and director-level cases at top</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="page-body">', unsafe_allow_html=True)

    # Fetch all escalated + critical
    data_esc, c1 = api_get("/admin/problems", {"escalated": "true"})
    data_crit, c2 = api_get("/admin/problems", {"priority": "critical"})

    # Merge and deduplicate
    all_ids = set()
    combined = []
    for d, c in [(data_esc, c1),(data_crit, c2)]:
        if c == 200:
            for p in d.get("problems",[]):
                if p["id"] not in all_ids:
                    all_ids.add(p["id"])
                    combined.append(p)

    # Sort: critical first, then by escalation level desc, then by date
    priority_order = {"critical":0,"high":1,"normal":2}
    combined.sort(key=lambda x: (
        priority_order.get(x.get("priority","normal"),2),
        -x.get("escalation_level",0),
        x.get("created_at",""),
    ))

    if not combined:
        st.markdown("""
        <div class="alert a-ok" style="margin-top:1rem">
          ✅ No escalated or critical complaints at this time. All clear!
        </div>""", unsafe_allow_html=True)
    else:
        # Summary counts
        crit_count = sum(1 for p in combined if p.get("priority")=="critical")
        dir_count  = sum(1 for p in combined if p.get("escalation_level",0) == 3)
        hw_count   = sum(1 for p in combined if p.get("escalation_level",0) == 2)
        w_count    = sum(1 for p in combined if p.get("escalation_level",0) == 1)

        st.markdown(f"""
        <div class="mtr-grid">
          <div class="mtr-card ml-red"><div class="mtr-label">🚨 Critical</div><div class="mtr-num">{crit_count}</div><div class="mtr-sub">medical + urgent</div></div>
          <div class="mtr-card ml-amber"><div class="mtr-label">🎓 At Director</div><div class="mtr-num">{dir_count}</div><div class="mtr-sub">highest level</div></div>
          <div class="mtr-card"><div class="mtr-label">👔 At Head Warden</div><div class="mtr-num">{hw_count}</div><div class="mtr-sub">level 2</div></div>
          <div class="mtr-card"><div class="mtr-label">👨‍💼 At Warden</div><div class="mtr-num">{w_count}</div><div class="mtr-sub">level 1</div></div>
        </div>""", unsafe_allow_html=True)

        for p in combined:
            priority = p.get("priority","normal")
            lv       = p.get("escalation_level",0)
            cat      = p.get("category","Other")
            status   = p.get("status","Submitted")
            p_meta   = PRIORITY_META.get(priority, PRIORITY_META["normal"])

            label_parts = [
                f"{p_meta['icon']} {p_meta['label']}",
                f"{p['tracking_id']}",
                f"{AUTHORITY_ICONS.get(p.get('current_authority',''),'🏢')} {p.get('current_authority','Department')}",
                f"{p['student_name']}",
                f"{CATEGORY_ICONS.get(cat,'')} {cat}",
            ]

            with st.expander("  ·  ".join(label_parts)):
                ci, ca = st.columns([3,2])
                with ci:
                    st.markdown(priority_banner(priority, p.get("is_medical",False), p.get("is_repeat",False)), unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="margin-bottom:.6rem">
                      <span class="tg-lbl">Tracking ID</span><br>
                      <span style="font-family:'JetBrains Mono',monospace;font-size:.9rem;color:var(--navy);font-weight:600">{p['tracking_id']}</span>
                    </div>""", unsafe_allow_html=True)

                    st.markdown(f"<div style='margin-bottom:.5rem'><div class='tg-lbl' style='margin-bottom:4px'>Escalation Path</div>{escalation_ladder_html(lv)}</div>", unsafe_allow_html=True)

                    if p.get("escalation_reason"):
                        st.markdown(f'<div class="alert a-purple" style="margin:.5rem 0">↑ {p["escalation_reason"]}<br><strong>Disputes filed: {p.get("dispute_count",0)}</strong></div>', unsafe_allow_html=True)

                    st.markdown(f"""
                    <div style="font-size:.76rem;color:var(--text-soft);margin-bottom:3px"><b>Student:</b> {p['student_name']} {'('+p['student_email']+')' if p.get('student_email') else ''}</div>
                    <div style="font-size:.76rem;color:var(--text-soft);margin-bottom:3px"><b>Department:</b> {p.get('department','—')}</div>
                    <div style="font-size:.76rem;color:var(--text-soft);margin-bottom:.6rem"><b>Submitted:</b> {str(p.get('created_at',''))[:19].replace('T',' ')}</div>
                    """, unsafe_allow_html=True)
                    st.markdown("**Complaint**")
                    st.info(p.get("description",""))
                    if p.get("resolution"):
                        st.success(f"**Last resolution attempt:** {p['resolution']}")

                with ca:
                    st.markdown('<div class="card"><div class="card-hdr">Update Status</div>', unsafe_allow_html=True)
                    idx  = ["Submitted","In Progress","Resolved","Rejected","Escalated"]
                    cur  = status if status in idx else "Submitted"
                    ns   = st.selectbox("Status", idx, index=idx.index(cur), key=f"esc_ns_{p['id']}")
                    rt   = st.text_area("Resolution / Comment", value=p.get("resolution",""),
                                        height=90, key=f"esc_rt_{p['id']}", placeholder="Detail the action taken...")
                    if st.button("💾 Save", key=f"esc_sv_{p['id']}", use_container_width=True):
                        resp, rc2 = api_put(f"/admin/problem/{p['id']}", {"status":ns,"resolution":rt})
                        if rc2 == 200: st.success("Updated!"); st.rerun()
                        else: st.error(resp.get("detail","Failed"))
                    st.markdown('</div>', unsafe_allow_html=True)

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

    f1, f2, f3, _, f4 = st.columns([2,2,2,1,1])
    with f1: fs = st.selectbox("Status",   ["All","Submitted","In Progress","Resolved","Rejected","Escalated"])
    with f2: fd = st.selectbox("Dept",     ["All","Housekeeping Department","Security & Discipline Cell","Mess Committee","Academic Office","Maintenance Department","General Administration"])
    with f3: fp = st.selectbox("Priority", ["All","critical","high","normal"])
    with f4:
        if st.button("🔄", use_container_width=True): st.rerun()

    params = {}
    if fs != "All": params["status"]   = fs
    if fd != "All": params["department"]= fd
    if fp != "All": params["priority"] = fp

    data, code = api_get("/admin/problems", params=params)
    if code != 200:
        st.markdown(f'<div class="alert a-err">Failed: {data.get("detail","")}</div>', unsafe_allow_html=True)
        st.stop()

    problems = data.get("problems",[])
    sc = {}
    for p in problems:
        s = p.get("status","Unknown"); sc[s] = sc.get(s,0)+1

    esc_count  = sum(1 for p in problems if p.get("escalation_level",0) > 0)
    crit_count = sum(1 for p in problems if p.get("priority")=="critical")

    st.markdown(f"""
    <div class="mtr-grid">
      <div class="mtr-card ml-blue"><div class="mtr-label">Loaded</div><div class="mtr-num">{len(problems)}</div><div class="mtr-sub">matching filters</div></div>
      <div class="mtr-card ml-red"><div class="mtr-label">🚨 Critical</div><div class="mtr-num">{crit_count}</div><div class="mtr-sub">needs immediate action</div></div>
      <div class="mtr-card ml-amber"><div class="mtr-label">⚡ Escalated</div><div class="mtr-num">{esc_count}</div><div class="mtr-sub">above department level</div></div>
      <div class="mtr-card ml-green"><div class="mtr-label">✅ Resolved</div><div class="mtr-num">{sc.get("Resolved",0)}</div><div class="mtr-sub">closed</div></div>
    </div>""", unsafe_allow_html=True)

    if not problems:
        st.markdown('<div class="alert a-info">No complaints found for the selected filters.</div>', unsafe_allow_html=True)
    else:
        for p in problems:
            status   = p.get("status","Submitted")
            cat      = p.get("category","Other")
            priority = p.get("priority","normal")
            lv       = p.get("escalation_level",0)
            p_meta   = PRIORITY_META.get(priority, PRIORITY_META["normal"])

            title = f"{p_meta['icon']} {p['tracking_id']}  ·  {p['student_name']}  ·  {CATEGORY_ICONS.get(cat,'')} {cat}  ·  {status}"
            if lv > 0:
                title += f"  ·  ↑ {p.get('current_authority','')}"

            with st.expander(title):
                ci, ca = st.columns([3,2])
                with ci:
                    st.markdown(priority_banner(priority, p.get("is_medical",False), p.get("is_repeat",False)), unsafe_allow_html=True)
                    if lv > 0:
                        st.markdown(f"<div class='tg-lbl' style='margin-bottom:4px'>Escalation Path</div>{escalation_ladder_html(lv)}", unsafe_allow_html=True)
                        if p.get("escalation_reason"):
                            st.markdown(f'<div class="alert a-purple" style="margin:.5rem 0">↑ {p["escalation_reason"]}</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="font-size:.76rem;color:var(--text-soft);margin:.5rem 0 3px"><b>Student:</b> {p['student_name']} {'('+p['student_email']+')' if p.get('student_email') else ''}</div>
                    <div style="font-size:.76rem;color:var(--text-soft);margin-bottom:3px"><b>Department:</b> {p.get('department','—')}</div>
                    <div style="font-size:.76rem;color:var(--text-soft);margin-bottom:.5rem"><b>Submitted:</b> {str(p.get('created_at',''))[:19].replace('T',' ')}</div>""", unsafe_allow_html=True)
                    st.markdown(f"<div class='tg-lbl' style='margin-bottom:4px'>AI Confidence</div>{cbar(p.get('confidence',0.75))}", unsafe_allow_html=True)
                    if p.get("reason"):
                        st.markdown(f'<div style="font-size:.71rem;color:var(--text-soft);margin-top:3px">AI: {p["reason"]}</div>', unsafe_allow_html=True)
                    st.markdown("<br>**Description**", unsafe_allow_html=True)
                    st.info(p.get("description",""))
                    if p.get("resolution"):
                        st.success(f"**Resolution:** {p['resolution']}")
                with ca:
                    st.markdown('<div class="card"><div class="card-hdr">Update Status</div>', unsafe_allow_html=True)
                    idx = ["Submitted","In Progress","Resolved","Rejected","Escalated"]
                    ns  = st.selectbox("Status", idx, index=idx.index(status) if status in idx else 0, key=f"ns_{p['id']}")
                    rt  = st.text_area("Resolution / Comment", value=p.get("resolution",""), height=90, key=f"rt_{p['id']}", placeholder="Detail the action taken...")
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
        <div class="ah-sub">Campus-wide complaint analytics including escalation data</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="page-body">', unsafe_allow_html=True)
    data, code = api_get("/admin/stats")
    if code != 200:
        st.markdown('<div class="alert a-err">Could not load statistics.</div>', unsafe_allow_html=True)
        st.stop()

    total          = data.get("total",0)
    by_status      = data.get("by_status",{})
    by_category    = data.get("by_category",{})
    by_dept        = data.get("by_department",{})
    by_authority   = data.get("by_authority",{})
    resolved       = by_status.get("Resolved",0)
    rr             = f"{int(resolved/total*100)}%" if total else "—"
    esc_cnt        = data.get("escalated_count",0)
    med_cnt        = data.get("medical_count",0)

    st.markdown(f"""
    <div class="mtr-grid">
      <div class="mtr-card ml-blue"><div class="mtr-label">Total Complaints</div><div class="mtr-num">{total}</div><div class="mtr-sub">all time</div></div>
      <div class="mtr-card ml-green"><div class="mtr-label">Resolved</div><div class="mtr-num">{resolved}</div><div class="mtr-sub">rate: {rr}</div></div>
      <div class="mtr-card ml-amber"><div class="mtr-label">⚡ Escalated</div><div class="mtr-num">{esc_cnt}</div><div class="mtr-sub">above department</div></div>
      <div class="mtr-card ml-red"><div class="mtr-label">🏥 Medical</div><div class="mtr-num">{med_cnt}</div><div class="mtr-sub">flagged critical</div></div>
    </div>""", unsafe_allow_html=True)

    l, r = st.columns(2, gap="large")
    with l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-hdr">By Category</div>', unsafe_allow_html=True)
        for cat, cnt in sorted(by_category.items(), key=lambda x:-x[1]):
            pct = int(cnt/total*100) if total else 0
            ic  = CATEGORY_ICONS.get(cat,"📋")
            st.markdown(f'<div class="bar-row"><div class="bar-top"><span class="bar-name">{ic} {cat}</span><span class="bar-cnt">{cnt} · {pct}%</span></div><div class="bar-bg"><div class="bar-fill" style="width:{pct}%;background:var(--navy)"></div></div></div>', unsafe_allow_html=True)
        if not by_category:
            st.markdown('<div class="alert a-info">No data yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-hdr">By Authority Level</div>', unsafe_allow_html=True)
        for auth, cnt in sorted(by_authority.items(), key=lambda x:-x[1]):
            pct  = int(cnt/total*100) if total else 0
            icon = AUTHORITY_ICONS.get(auth,"🏢")
            st.markdown(f'<div class="bar-row"><div class="bar-top"><span class="bar-name">{icon} {auth}</span><span class="bar-cnt">{cnt} · {pct}%</span></div><div class="bar-bg"><div class="bar-fill" style="width:{pct}%;background:var(--amber)"></div></div></div>', unsafe_allow_html=True)
        if not by_authority:
            st.markdown('<div class="alert a-info">No data yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    status_colors_m = {"Submitted":"#2563EB","In Progress":"#D97706","Resolved":"#059669","Rejected":"#DC2626","Escalated":"#7C3AED"}
    sb_html = '<div class="card" style="margin-top:1rem"><div class="card-hdr">Status Breakdown</div><div class="sb-grid">'
    for s in ["Submitted","In Progress","Escalated","Resolved","Rejected"]:
        cnt = by_status.get(s,0); pct = int(cnt/total*100) if total else 0
        c   = status_colors_m.get(s,"#64748B")
        sb_html += f'<div class="sb-card"><div class="sb-num" style="color:{c}">{cnt}</div><div class="sb-lbl">{s}</div><div class="sb-pct">{pct}%</div></div>'
    sb_html += '</div></div>'
    st.markdown(sb_html, unsafe_allow_html=True)

    if st.button("🔄 Refresh"): st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="portal-footer">
  <span>CampusGriev</span> · Student Grievance Management System ·
  Powered by <span>LLaMA 3.1</span> via Groq · <span>All complaints are confidential</span>
</div>""", unsafe_allow_html=True)
