from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Campus Solver API")

# Allow frontend to talk to backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq AI client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize Supabase database client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ── Data Models ──────────────────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    student_name: str
    question: str
    subject: str = "General"

class QuestionResponse(BaseModel):
    id: int
    student_name: str
    question: str
    answer: str
    subject: str

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "Campus Solver API is running!"}


@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    """
    Receives a question, gets an AI answer from Groq,
    saves everything to Supabase, and returns the result.
    """

    # Validate input
    if not request.student_name.strip():
        raise HTTPException(status_code=400, detail="Student name cannot be empty.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Step 1: Ask Groq AI for an answer
    try:
        chat_response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",   # Fast, free Llama 3 model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful academic assistant for university students. "
                        "Give clear, concise, and accurate answers. "
                        "If a question is about a specific subject, tailor your explanation "
                        "to that subject. Keep answers under 300 words."
                    )
                },
                {
                    "role": "user",
                    "content": f"Subject: {request.subject}\n\nQuestion: {request.question}"
                }
            ],
            temperature=0.7,
            max_tokens=512,
        )
        ai_answer = chat_response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

    # Step 2: Save the question and answer to Supabase
    try:
        db_response = supabase.table("questions").insert({
            "student_name": request.student_name.strip(),
            "question": request.question.strip(),
            "answer": ai_answer,
            "subject": request.subject.strip(),
        }).execute()

        saved_record = db_response.data[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Step 3: Return the saved record
    return QuestionResponse(
        id=saved_record["id"],
        student_name=saved_record["student_name"],
        question=saved_record["question"],
        answer=saved_record["answer"],
        subject=saved_record["subject"],
    )


@app.get("/history")
def get_history(limit: int = 20):
    """Fetch the most recent questions and answers from the database."""
    try:
        response = supabase.table("questions") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return {"questions": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.delete("/question/{question_id}")
def delete_question(question_id: int):
    """Delete a specific question by ID."""
    try:
        supabase.table("questions").delete().eq("id", question_id).execute()
        return {"message": f"Question {question_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")