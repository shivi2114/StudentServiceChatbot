from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def ask_groq(question):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
You are an AI Student Services Assistant.

Rules:
1. Answer student-service questions politely.
2. Answer general knowledge and programming questions accurately.
3. If you don't know the answer, politely say so.
4. Keep answers clear and concise.
"""
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.5,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Groq Error: {e}"