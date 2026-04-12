from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client
from dotenv import load_dotenv
import os, uuid, json
from datetime import datetime, timezone

load_dotenv()

app = FastAPI(title="Campus Problem Solver API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ── Category → Department Routing Map ────────────────────────────────────────
DEPARTMENT_MAP = {
    "Bathroom & Hygiene":        "Housekeeping Department",
    "Anti-Ragging & Safety":     "Security & Discipline Cell",
    "Mess & Food Quality":       "Mess Committee",
    "Academic Issues":           "Academic Office",
    "Infrastructure/Maintenance":"Maintenance Department",
    "Other":                     "General Administration",
}
CATEGORIES = list(DEPARTMENT_MAP.keys())

# ── Pydantic Models ───────────────────────────────────────────────────────────
class ProblemRequest(BaseModel):
    student_name: str
    student_email: str = ""
    description: str

class StatusUpdate(BaseModel):
    status: str
    resolution: str = ""

# ── Helper: Classify with Groq ────────────────────────────────────────────────
def classify_problem(description: str) -> dict:
    category_list = "\n".join(f"{i+1}. {c}" for i, c in enumerate(CATEGORIES))
    prompt = f"""You are a campus complaint classifier. Classify the problem below into exactly one category.

Categories:
{category_list}

Problem: "{description}"

Rules:
- Choose the single most relevant category
- Confidence must be between 0.0 and 1.0
- If unsure, use "Other" with confidence 0.5

Respond ONLY with valid JSON, no extra text:
{{"category": "<category name>", "confidence": <number>, "reason": "<one sentence>"}}"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=120,
        )
        raw = resp.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        # Extract JSON if surrounded by extra text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]
        result = json.loads(raw)
        category = result.get("category", "Other")
        confidence = float(result.get("confidence", 0.75))
        reason = result.get("reason", "")
        if category not in CATEGORIES:
            category = "Other"
            confidence = 0.5
        return {"category": category, "confidence": round(confidence, 2), "reason": reason}
    except Exception:
        return {"category": "Other", "confidence": 0.5, "reason": "Could not classify automatically"}

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Campus Problem Solver API is running!"}


@app.post("/submit")
def submit_problem(req: ProblemRequest):
    if not req.student_name.strip():
        raise HTTPException(400, "Student name is required.")
    if not req.description.strip() or len(req.description.strip()) < 10:
        raise HTTPException(400, "Problem description must be at least 10 characters.")

    # Step 1: Classify
    classification = classify_problem(req.description)
    category   = classification["category"]
    confidence = classification["confidence"]
    reason     = classification["reason"]

    # Step 2: Route to department
    department = DEPARTMENT_MAP.get(category, "General Administration")

    # Step 3: Generate tracking ID
    tracking_id = f"CPS-{uuid.uuid4().hex[:8].upper()}"

    # Step 4: Save to database
    try:
        db_resp = supabase.table("problems").insert({
            "tracking_id":   tracking_id,
            "student_name":  req.student_name.strip(),
            "student_email": req.student_email.strip(),
            "description":   req.description.strip(),
            "category":      category,
            "confidence":    confidence,
            "reason":        reason,
            "department":    department,
            "status":        "Submitted",
            "resolution":    "",
        }).execute()
        record = db_resp.data[0]
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")

    return {
        "tracking_id": tracking_id,
        "category":    category,
        "confidence":  confidence,
        "department":  department,
        "status":      "Submitted",
        "message":     f"Problem submitted successfully! Your Tracking ID is {tracking_id}",
    }


@app.get("/track/{tracking_id}")
def track_problem(tracking_id: str):
    try:
        resp = supabase.table("problems") \
            .select("*") \
            .eq("tracking_id", tracking_id.upper().strip()) \
            .execute()
        if not resp.data:
            raise HTTPException(404, f"No problem found with tracking ID '{tracking_id}'.")
        return resp.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")


@app.get("/admin/problems")
def get_all_problems(status: str = None, department: str = None):
    try:
        query = supabase.table("problems").select("*").order("created_at", desc=True)
        if status:
            query = query.eq("status", status)
        if department:
            query = query.eq("department", department)
        resp = query.execute()
        return {"problems": resp.data, "total": len(resp.data)}
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")


@app.put("/admin/problem/{problem_id}")
def update_problem(problem_id: int, update: StatusUpdate):
    valid_statuses = ["Submitted", "In Progress", "Resolved", "Rejected"]
    if update.status not in valid_statuses:
        raise HTTPException(400, f"Status must be one of: {valid_statuses}")
    try:
        resp = supabase.table("problems").update({
            "status":     update.status,
            "resolution": update.resolution,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", problem_id).execute()
        if not resp.data:
            raise HTTPException(404, "Problem not found.")
        return resp.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Update error: {str(e)}")


@app.get("/admin/stats")
def get_stats():
    try:
        resp = supabase.table("problems").select("category, status, department").execute()
        data = resp.data
        by_status     = {}
        by_category   = {}
        by_department = {}
        for row in data:
            s = row.get("status", "Unknown")
            c = row.get("category", "Unknown")
            d = row.get("department", "Unknown")
            by_status[s]     = by_status.get(s, 0) + 1
            by_category[c]   = by_category.get(c, 0) + 1
            by_department[d] = by_department.get(d, 0) + 1
        return {
            "total":         len(data),
            "by_status":     by_status,
            "by_category":   by_category,
            "by_department": by_department,
        }
    except Exception as e:
        raise HTTPException(500, f"Stats error: {str(e)}")