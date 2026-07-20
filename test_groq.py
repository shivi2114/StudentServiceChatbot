from groq_chat import ask_groq

question = input("Ask a question: ")

answer = ask_groq(question)

print("\nAI Answer:\n")
print(answer)