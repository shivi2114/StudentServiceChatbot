import pickle
import pandas as pd
import random

from utils import clean_text
from groq_chat import ask_groq

# ==========================
# Load ML Model
# ==========================

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open("label_encoder.pkl", "rb") as f:
    encoder = pickle.load(f)

# ==========================
# Load Dataset
# ==========================

df = pd.read_csv("student_services_dataset_17000_plus.csv")

# ==========================
# Chatbot Function
# ==========================

def get_response(question):
    try:
        # Clean user input
        clean = clean_text(question)

        # Convert to TF-IDF vector
        vector = vectorizer.transform([clean])

        # Predict intent
        prediction = model.predict(vector)
        intent = encoder.inverse_transform(prediction)[0]

        # Get confidence score
        confidence = model.predict_proba(vector).max()

        print(f"Predicted Intent: {intent}")
        print(f"Confidence: {confidence:.2f}")

        # If confidence is high, use ML dataset
        if confidence >= 0.70:

            answers = df[df["intent"] == intent]["answer"].tolist()

            if answers:
                return random.choice(answers)

        # Otherwise use Groq AI
        return ask_groq(question)

    except Exception as e:
        return f" Error: {str(e)}"