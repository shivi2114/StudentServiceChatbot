import os
from config import GROQ_API_KEY, GROQ_MODEL, has_groq_api_key

_client = None

SYSTEM_PROMPT = """You are the official Student Services Assistant for the college.
Your role is to help students with questions about campus admissions, courses, fees, schedules, campus facilities, and department contacts.

Core Guidelines:
1. Rely only on established college student service policies and verified campus offices:
   - Admission Cell: Application forms, eligibility, document verification.
   - Accounts Office: Tuition fees, ERP online fee payments, fee refund policies.
   - Central Library: Book issue and return (using library card), open 9:00 AM to 5:00 PM on working days.
   - Examination Cell: Semester exam schedules, results on university portal, revaluation, back paper registration.
   - Academic Departments: Timetables, lab schedules, syllabus, leave applications (via mentor/HOD), project coordinators.
   - Hostel Office: Room allotment based on availability and rules, hostel fee structure, mess timings and menu.
   - IT Support Desk: Student ERP portal login, campus Wi-Fi credentials, password resets.
   - Student Affairs & Admin: Bonafide certificates, character certificates, migration certificates, new/duplicate ID cards.
   - Training & Placement Cell: Campus placement drives, internship opportunities, training sessions.
   - Student Welfare & Grievance Cell: Scholarship Cell, Anti-Ragging Committee, confidential grievance resolution.
   - Transport Office: Bus routes, timings, and transport fees.
   - Campus Facilities: Health center (working hours), sports department, student clubs, cafeteria.
   - College Reception: General campus enquiries and visitors.

2. Never invent, guess, or fabricate:
   - Specific fee amounts, deadlines, or dates that are not provided.
   - Unverified phone numbers, email addresses, or bank account details.
   - Fake academic policies or admission guarantees.

3. If an exact answer, date, or fee amount is not known, state clearly and plainly:
   "I do not have that specific record on file. Please contact the [Relevant Office] or visit the College Reception for verified details."

4. Answer politely, concisely, and in natural, student-friendly language. Avoid repetitive filler or robotic phrasing.

5. If a question is completely unrelated to college or student life (such as coding assignments or general trivia), politely explain that this assistant is dedicated to college student services and guide the student back to campus-related queries.
"""

FALLBACK_MODELS = [GROQ_MODEL, "qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]


def get_groq_client():
    """Lazily initialize and return the Groq client, or None if unavailable."""
    global _client
    if _client is not None:
        return _client

    if not has_groq_api_key():
        return None

    try:
        from groq import Groq
        _client = Groq(api_key=GROQ_API_KEY)
        return _client
    except Exception as e:
        print(f"Error initializing Groq client: {e}")
        return None


def ask_groq(question: str, history: list = None) -> str:
    """Send a query to Groq with optional conversation history and grounded system prompt."""
    client = get_groq_client()
    if client is None:
        return (
            "I am currently operating in offline mode. For assistance with this inquiry, "
            "please visit the College Reception or check with your department office."
        )

    # Build messages array
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Include recent conversation turns for context (up to last 6 messages)
    if history:
        recent_history = history[-6:]
        for msg in recent_history:
            role = msg.get("role")
            content = msg.get("content", "").strip()
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    # Add the current question
    messages.append({"role": "user", "content": question})

    # Deduplicate fallback models while preserving order
    models_to_try = []
    for m in FALLBACK_MODELS:
        if m and m not in models_to_try:
            models_to_try.append(m)

    last_error = None
    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.3,
                max_tokens=400,
            )
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
        except Exception as e:
            last_error = e
            # Try next model if it was a model-not-found or invalid request
            print(f"Groq call with model '{model_name}' failed: {e}")
            continue

    print(f"All Groq model attempts failed. Last error: {last_error}")
    return (
        "I could not look that up at the moment. For immediate guidance, please check with the "
        "College Reception or the relevant campus office."
    )
