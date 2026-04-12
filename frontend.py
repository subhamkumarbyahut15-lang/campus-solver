import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────
# During development in Codespaces, use localhost.
# After deploying to Render, change this to your Render URL.
BACKEND_URL = os.getenv("BACKEND_URL", "https://campus-solver-api.onrender.com")

SUBJECTS = [
    "General",
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Computer Science",
    "History",
    "Literature",
    "Economics",
    "Engineering",
]

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Campus Solver",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
    }
    .stButton > button:hover { background-color: #155a8a; }
    .answer-box {
        background-color: #f0f8ff;
        border-left: 5px solid #1f77b4;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1rem;
    }
    .history-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.07);
    }
    .subject-badge {
        background: #1f77b4;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎓 Campus Solver")
    st.markdown("---")
    st.markdown("**Your AI-powered academic assistant.**")
    st.markdown("Ask any question and get an instant answer from Llama 3.")
    st.markdown("---")

    # Quick health check
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=5)
        if r.status_code == 200:
            st.success("✅ Backend connected")
        else:
            st.error("❌ Backend error")
    except:
        st.error("❌ Cannot reach backend.\nMake sure it is running.")

    st.markdown("---")
    st.caption("Built with FastAPI + Streamlit + Groq + Supabase")

# ── Main Layout ───────────────────────────────────────────────────────────────
st.title("🎓 Campus Solver")
st.subheader("Ask any academic question — get an AI answer instantly.")
st.markdown("---")

tab1, tab2 = st.tabs(["💬 Ask a Question", "📚 Question History"])

# ── Tab 1: Ask ────────────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        student_name = st.text_input(
            "Your Name",
            placeholder="e.g. Rahul Sharma",
            help="Enter your name so we can personalize the response."
        )

    with col2:
        subject = st.selectbox("Subject", SUBJECTS)

    question = st.text_area(
        "Your Question",
        placeholder="e.g. Explain Newton's Second Law of Motion with an example.",
        height=130,
    )

    if st.button("🚀 Get Answer"):
        if not student_name.strip():
            st.warning("Please enter your name.")
        elif not question.strip():
            st.warning("Please type a question.")
        else:
            with st.spinner("Getting your answer from AI..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/ask",
                        json={
                            "student_name": student_name.strip(),
                            "question": question.strip(),
                            "subject": subject,
                        },
                        timeout=30,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.success("✅ Answer received!")
                        st.markdown(
                            f'<div class="answer-box">'
                            f'<strong>Answer for {data["student_name"]}:</strong><br><br>'
                            f'{data["answer"]}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        st.caption(f"Subject: {data['subject']} | Record ID: #{data['id']}")
                    else:
                        err = response.json().get("detail", "Unknown error")
                        st.error(f"Error from server: {err}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend. Is it running?")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

# ── Tab 2: History ────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Recent Questions & Answers")

    col_refresh, col_limit = st.columns([1, 1])
    with col_limit:
        limit = st.slider("How many to show", 5, 50, 10)

    if st.button("🔄 Refresh History"):
        st.rerun()

    try:
        response = requests.get(f"{BACKEND_URL}/history?limit={limit}", timeout=10)
        if response.status_code == 200:
            questions = response.json().get("questions", [])
            if not questions:
                st.info("No questions yet. Ask the first one!")
            else:
                st.markdown(f"Showing **{len(questions)}** most recent questions.")
                for q in questions:
                    with st.expander(f"#{q['id']} — {q['student_name']}: {q['question'][:80]}..."):
                        st.markdown(
                            f'<span class="subject-badge">{q["subject"]}</span>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"**Question:** {q['question']}")
                        st.markdown("**Answer:**")
                        st.markdown(
                            f'<div class="answer-box">{q["answer"]}</div>',
                            unsafe_allow_html=True,
                        )
                        st.caption(f"Asked at: {q.get('created_at', 'N/A')[:19].replace('T', ' ')}")
        else:
            st.error("Failed to fetch history.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend.")
    except Exception as e:
        st.error(f"Error loading history: {e}")