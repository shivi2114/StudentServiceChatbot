import os
from typing import List, Dict, Any, Optional
from backend.app.config import settings

# Global client cache
_gemini_client = None
_groq_client = None


def get_gemini_client():
    """Lazily initialize Google Gemini client."""
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client

    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from google import genai
        _gemini_client = genai.Client(api_key=api_key)
        return _gemini_client
    except Exception as e:
        print(f"[CampusAI] Gemini initialization error: {e}")
        return None


def get_groq_client():
    """Lazily initialize Groq client as secondary fallback."""
    global _groq_client
    if _groq_client is not None:
        return _groq_client

    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from groq import Groq
        _groq_client = Groq(api_key=api_key)
        return _groq_client
    except Exception as e:
        print(f"[CampusAI] Groq fallback initialization error: {e}")
        return None


def call_llm(
    prompt: str,
    system_instruction: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
    temperature: float = 0.2,
    max_tokens: int = 600
) -> str:
    """
    Query LLM with multi-tier resilience:
    Tier 1: Google Gemini (2.5-flash / configured model)
    Tier 2: Groq API fallback
    Tier 3: Graceful institutional referral fallback
    """
    default_system = (
        system_instruction or
        "You are CampusAI, an official university student assistant. "
        "Provide factual, helpful, and concise guidance based on institutional policies. "
        "Never fabricate deadlines, marks, fees, or policy rules."
    )

    # ---------------------------------------------
    # Tier 1: Google Gemini API
    # ---------------------------------------------
    gemini_client = get_gemini_client()
    if gemini_client is not None:
        try:
            full_prompt = f"{default_system}\n\nStudent Query: {prompt}"
            if history:
                context_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-4:]])
                full_prompt = f"{default_system}\n\nRecent Conversation:\n{context_str}\n\nStudent Query: {prompt}"

            response = gemini_client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=full_prompt,
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"[CampusAI] Gemini call failed ({e}), attempting Groq fallback...")

    # ---------------------------------------------
    # Tier 2: Groq Fallback
    # ---------------------------------------------
    groq_client = get_groq_client()
    if groq_client is not None:
        try:
            messages = [{"role": "system", "content": default_system}]
            if history:
                for h in history[-4:]:
                    if h.get("role") in ("user", "assistant") and h.get("content"):
                        messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": prompt})

            res = groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = res.choices[0].message.content
            if content and content.strip():
                return content.strip()
        except Exception as e:
            print(f"[CampusAI] Groq fallback failed: {e}")

    # ---------------------------------------------
    # Tier 3: Local Grounded Safety Fallback
    # ---------------------------------------------
    return (
        "I am currently operating in safe institutional reference mode. "
        "For official records, dates, and verification, please consult your Class Mentor, "
        "the Examination Cell (Ground Floor Counter 3), or the Student Helpdesk."
    )
