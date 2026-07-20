import re
import string

import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download only if not already present
try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

try:
    lemmatizer = WordNetLemmatizer()
    lemmatizer.lemmatize("students")
except LookupError:
    nltk.download("wordnet")
    nltk.download("omw-1.4")
    lemmatizer = WordNetLemmatizer()


def clean_text(text):

    text = text.lower()

    text = re.sub(r"\d+","",text)

    text = text.translate(
        str.maketrans("","",string.punctuation)
    )

    words = text.split()

    words = [word for word in words if word not in stop_words]

    words = [lemmatizer.lemmatize(word) for word in words]

    return " ".join(words)