# 🎓 Campus Problem Solver

An AI-powered campus complaint management system built with FastAPI, Streamlit, Groq (LLaMA 3), and Supabase.

## 🚀 Live Demo
- **Frontend**: [your-streamlit-url.streamlit.app]
- **Backend API**: [your-render-url.onrender.com]

## 🧠 Features
| Feature | Status |
|---|---|
| Problem Submission Portal | ✅ |
| AI Classification (6 categories) | ✅ |
| Confidence Score | ✅ |
| Auto-routing to Department | ✅ |
| Admin Dashboard | ✅ |
| Student Tracking Dashboard | ✅ |
| Real-time Status Updates | ✅ |
| Statistics Dashboard | ✅ |

## 🏷️ Classification Categories
1. 🚽 Bathroom & Hygiene → Housekeeping Department
2. 🛡️ Anti-Ragging & Safety → Security & Discipline Cell
3. 🍽️ Mess & Food Quality → Mess Committee
4. 📚 Academic Issues → Academic Office
5. 🔧 Infrastructure/Maintenance → Maintenance Department
6. 📌 Other → General Administration

## 🤖 AI Agent
- Model: LLaMA 3.1 8B via Groq API
- Target accuracy: ≥75% (confidence score returned per classification)
- Fallback: Defaults to "Other" category if confidence < 50%

## 🛠️ Tech Stack
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit
- **AI**: Groq (LLaMA 3.1 8B Instant)
- **Database**: Supabase (PostgreSQL)
- **Hosting**: Render (backend) + Streamlit Cloud (frontend)

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/campus-solver
cd campus-solver
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
Create a `.env` file:
```
GROQ_API_KEY=your_groq_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
BACKEND_URL=http://localhost:8000
ADMIN_PASSWORD=admin123
```

### 4. Set up the database
Run `schema.sql` in your Supabase SQL Editor.

### 5. Run locally
```bash
# Terminal 1 — Backend
uvicorn backend:app --reload

# Terminal 2 — Frontend
streamlit run frontend.py
```

## 📊 Classification Accuracy
The AI agent uses prompt engineering with LLaMA 3.1 to classify complaints.
Accuracy is documented per submission via the confidence score (target ≥75%).
Low-confidence results (<50%) automatically fall back to "Other" category.

## 🔐 Admin Access
Default password: `admin123`
Set `ADMIN_PASSWORD` environment variable to change it.