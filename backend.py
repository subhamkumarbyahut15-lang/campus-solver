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
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ── Constants ─────────────────────────────────────────────────────────────────

DEPARTMENT_MAP = {
    "Bathroom & Hygiene":         "Housekeeping Department",
    "Anti-Ragging & Safety":      "Security & Discipline Cell",
    "Mess & Food Quality":        "Mess Committee",
    "Academic Issues":            "Academic Office",
    "Infrastructure/Maintenance": "Maintenance Department",
    "Other":                      "General Administration",
}
CATEGORIES = list(DEPARTMENT_MAP.keys())

# Escalation ladder: level → authority name
ESCALATION_LADDER = {
    0: "Department",
    1: "Warden",
    2: "Head Warden",
    3: "Director",
}

# Medical keywords — any match → is_medical = True → priority = critical
MEDICAL_KEYWORDS = [
    "hospital", "doctor", "medical", "ambulance", "injury", "injured",
    "accident", "sick", "illness", "health", "medicine", "clinic",
    "blood", "emergency", "fever", "unconscious", "faint", "fracture",
    "wound", "pain", "ache", "suffering", "admitted", "ward",
]

# Repeat threshold: if same category from same email in last 30 days ≥ this → is_repeat = True
REPEAT_THRESHOLD = 2

# Auto-escalation rules:
# dispute_count >= 1 → escalate one level
# dispute_count >= 3 → skip to Head Warden
# dispute_count >= 5 → escalate to Director
# is_medical         → always critical, start at Warden
# is_repeat          → priority = high

# ── Models ────────────────────────────────────────────────────────────────────

class ProblemRequest(BaseModel):
    student_name:  str
    student_email: str = ""
    description:   str

class StatusUpdate(BaseModel):
    status:     str
    resolution: str = ""

class DisputeRequest(BaseModel):
    reason: str = "Student reports issue is not resolved"

# ── Helpers ───────────────────────────────────────────────────────────────────

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
        raw = raw.replace("```json","").replace("```","").strip()
        s = raw.find("{"); e = raw.rfind("}") + 1
        if s != -1 and e > s:
            raw = raw[s:e]
        result     = json.loads(raw)
        category   = result.get("category","Other")
        confidence = float(result.get("confidence", 0.75))
        reason     = result.get("reason","")
        if category not in CATEGORIES:
            category, confidence = "Other", 0.5
        return {"category": category, "confidence": round(confidence,2), "reason": reason}
    except Exception:
        return {"category": "Other", "confidence": 0.5, "reason": "Could not classify automatically"}


def detect_medical(description: str) -> bool:
    desc_lower = description.lower()
    return any(kw in desc_lower for kw in MEDICAL_KEYWORDS)


def detect_repeat(email: str, category: str) -> bool:
    """Returns True if this student (by email) has filed 2+ complaints
    in the same category that are still unresolved."""
    if not email.strip():
        return False
    try:
        resp = supabase.table("problems") \
            .select("id") \
            .eq("student_email", email.strip()) \
            .eq("category", category) \
            .neq("status", "Resolved") \
            .execute()
        return len(resp.data) >= REPEAT_THRESHOLD
    except Exception:
        return False


def compute_priority(is_medical: bool, is_repeat: bool) -> str:
    if is_medical:
        return "critical"
    if is_repeat:
        return "high"
    return "normal"


def escalate_record(problem_id: int, current_level: int, reason: str) -> dict:
    """Push a complaint one level up the hierarchy. Returns updated record."""
    new_level     = min(current_level + 1, 3)
    new_authority = ESCALATION_LADDER[new_level]
    now           = datetime.now(timezone.utc).isoformat()

    resp = supabase.table("problems").update({
        "escalation_level":  new_level,
        "current_authority": new_authority,
        "escalation_reason": reason,
        "status":            "Escalated",
        "updated_at":        now,
        "escalated_at":      now,
    }).eq("id", problem_id).execute()

    return resp.data[0] if resp.data else {}

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Campus Problem Solver API is running!"}


@app.post("/submit")
def submit_problem(req: ProblemRequest):
    if not req.student_name.strip():
        raise HTTPException(400, "Student name is required.")
    if len(req.description.strip()) < 10:
        raise HTTPException(400, "Description must be at least 10 characters.")

    # 1 — AI classify
    clf        = classify_problem(req.description)
    category   = clf["category"]
    confidence = clf["confidence"]
    reason     = clf["reason"]
    department = DEPARTMENT_MAP.get(category, "General Administration")

    # 2 — Detect medical & repeat
    is_medical = detect_medical(req.description)
    is_repeat  = detect_repeat(req.student_email, category)
    priority   = compute_priority(is_medical, is_repeat)

    # 3 — If medical, start escalated at Warden immediately
    if is_medical:
        init_level     = 1
        init_authority = "Warden"
        esc_reason     = "Auto-escalated: Medical issue detected by AI"
        init_status    = "Escalated"
    else:
        init_level     = 0
        init_authority = "Department"
        esc_reason     = ""
        init_status    = "Submitted"

    # 4 — Tracking ID
    tracking_id = f"CPS-{uuid.uuid4().hex[:8].upper()}"
    now         = datetime.now(timezone.utc).isoformat()

    # 5 — Insert
    try:
        row = supabase.table("problems").insert({
            "tracking_id":       tracking_id,
            "student_name":      req.student_name.strip(),
            "student_email":     req.student_email.strip(),
            "description":       req.description.strip(),
            "category":          category,
            "confidence":        confidence,
            "reason":            reason,
            "department":        department,
            "status":            init_status,
            "resolution":        "",
            "escalation_level":  init_level,
            "current_authority": init_authority,
            "escalation_reason": esc_reason,
            "dispute_count":     0,
            "priority":          priority,
            "is_medical":        is_medical,
            "is_repeat":         is_repeat,
            "escalated_at":      now if is_medical else None,
        }).execute()
        record = row.data[0]
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")

    return {
        "tracking_id":       tracking_id,
        "category":          category,
        "confidence":        confidence,
        "department":        department,
        "status":            init_status,
        "priority":          priority,
        "is_medical":        is_medical,
        "is_repeat":         is_repeat,
        "current_authority": init_authority,
        "escalation_level":  init_level,
        "message":           f"Submitted. Tracking ID: {tracking_id}",
    }


@app.get("/track/{tracking_id}")
def track_problem(tracking_id: str):
    try:
        resp = supabase.table("problems") \
            .select("*") \
            .eq("tracking_id", tracking_id.upper().strip()) \
            .execute()
        if not resp.data:
            raise HTTPException(404, f"No problem found with ID '{tracking_id}'.")
        return resp.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")


@app.post("/dispute/{tracking_id}")
def dispute_resolution(tracking_id: str, req: DisputeRequest):
    """
    Called when a student marks a 'Resolved' complaint as still unresolved.
    Increments dispute_count and escalates up the hierarchy automatically.
    """
    # Fetch the record
    resp = supabase.table("problems") \
        .select("*") \
        .eq("tracking_id", tracking_id.upper().strip()) \
        .execute()
    if not resp.data:
        raise HTTPException(404, "Complaint not found.")

    p             = resp.data[0]
    current_level = p.get("escalation_level", 0)
    dispute_count = p.get("dispute_count", 0) + 1

    # Determine new escalation level based on dispute count
    if dispute_count >= 5:
        new_level = 3   # Director
    elif dispute_count >= 3:
        new_level = 2   # Head Warden
    else:
        new_level = min(current_level + 1, 3)

    new_authority = ESCALATION_LADDER[new_level]
    esc_reason    = f"Dispute #{dispute_count}: {req.reason.strip() or 'Student reports issue unresolved'}"
    now           = datetime.now(timezone.utc).isoformat()

    # Update
    try:
        upd = supabase.table("problems").update({
            "dispute_count":     dispute_count,
            "escalation_level":  new_level,
            "current_authority": new_authority,
            "escalation_reason": esc_reason,
            "status":            "Escalated",
            "resolution":        "",          # clear old resolution — needs re-review
            "updated_at":        now,
            "escalated_at":      now,
        }).eq("tracking_id", tracking_id.upper().strip()).execute()
        record = upd.data[0]
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")

    return {
        "tracking_id":       tracking_id.upper(),
        "dispute_count":     dispute_count,
        "escalation_level":  new_level,
        "current_authority": new_authority,
        "status":            "Escalated",
        "message":           f"Complaint escalated to {new_authority}. They will review your case.",
    }


@app.get("/admin/problems")
def get_all_problems(status: str = None, department: str = None,
                     priority: str = None, escalated: bool = None):
    try:
        query = supabase.table("problems").select("*").order("priority", desc=True)

        # Secondary sort trick: fetch all, sort in Python for multi-key sort
        if status:
            query = query.eq("status", status)
        if department:
            query = query.eq("department", department)
        if priority:
            query = query.eq("priority", priority)
        if escalated is True:
            query = query.gt("escalation_level", 0)

        resp = query.order("created_at", desc=True).execute()
        data = resp.data

        # Sort: critical first, then high, then escalated, then by date
        priority_order = {"critical": 0, "high": 1, "normal": 2}
        data.sort(key=lambda x: (
            priority_order.get(x.get("priority","normal"), 2),
            -x.get("escalation_level", 0),
            x.get("created_at",""),
        ))

        return {"problems": data, "total": len(data)}
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")


@app.put("/admin/problem/{problem_id}")
def update_problem(problem_id: int, update: StatusUpdate):
    valid = ["Submitted","In Progress","Resolved","Rejected","Escalated"]
    if update.status not in valid:
        raise HTTPException(400, f"Status must be one of: {valid}")
    try:
        now = datetime.now(timezone.utc).isoformat()
        resp = supabase.table("problems").update({
            "status":     update.status,
            "resolution": update.resolution,
            "updated_at": now,
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
        resp = supabase.table("problems").select(
            "category, status, department, priority, escalation_level, is_medical, is_repeat"
        ).execute()
        data = resp.data

        by_status      = {}
        by_category    = {}
        by_department  = {}
        by_priority    = {}
        by_authority   = {}
        medical_count  = 0
        repeat_count   = 0
        escalated_count= 0

        for row in data:
            s  = row.get("status","Unknown")
            c  = row.get("category","Unknown")
            d  = row.get("department","Unknown")
            pr = row.get("priority","normal")
            lv = row.get("escalation_level", 0)
            au = ESCALATION_LADDER.get(lv, "Department")

            by_status[s]     = by_status.get(s, 0) + 1
            by_category[c]   = by_category.get(c, 0) + 1
            by_department[d] = by_department.get(d, 0) + 1
            by_priority[pr]  = by_priority.get(pr, 0) + 1
            by_authority[au] = by_authority.get(au, 0) + 1

            if row.get("is_medical"):  medical_count  += 1
            if row.get("is_repeat"):   repeat_count   += 1
            if lv > 0:                 escalated_count+= 1

        return {
            "total":            len(data),
            "by_status":        by_status,
            "by_category":      by_category,
            "by_department":    by_department,
            "by_priority":      by_priority,
            "by_authority":     by_authority,
            "medical_count":    medical_count,
            "repeat_count":     repeat_count,
            "escalated_count":  escalated_count,
        }
    except Exception as e:
        raise HTTPException(500, f"Stats error: {str(e)}")