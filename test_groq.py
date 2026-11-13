from groq_chat import ask_groq

if __name__ == "__main__":
    print("=== Student Services AI Test Console ===")
    question = input("Ask a campus question: ").strip()
    if not question:
        question = "How do I pay my semester fees?"
        print(f"Using sample question: {question}")

    answer = ask_groq(question)
    print("\nAssistant Answer:\n")
    print(answer)
