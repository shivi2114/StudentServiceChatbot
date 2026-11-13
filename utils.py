import re
import string

# ==============================================================================
# Robust Token Preprocessing: NLTK with Built-In Fallback
# ==============================================================================

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer

    try:
        stop_words = set(stopwords.words("english"))
    except (LookupError, Exception):
        try:
            nltk.download("stopwords", quiet=True)
            stop_words = set(stopwords.words("english"))
        except Exception:
            stop_words = None

    try:
        lemmatizer = WordNetLemmatizer()
        lemmatizer.lemmatize("students")
    except (LookupError, Exception):
        try:
            nltk.download("wordnet", quiet=True)
            nltk.download("omw-1.4", quiet=True)
            lemmatizer = WordNetLemmatizer()
        except Exception:
            lemmatizer = None

    if stop_words is None:
        raise ImportError("NLTK stopwords unavailable")

    def _lemmatize_word(word: str) -> str:
        if lemmatizer is not None:
            try:
                return lemmatizer.lemmatize(word)
            except Exception:
                pass
        return word

except (ImportError, ModuleNotFoundError, Exception):
    # Standalone fallback: ensures the app runs smoothly even if NLTK is
    # not installed in the global Python environment.
    stop_words = {
        "a", "about", "above", "after", "again", "against", "ain", "all", "am", "an", "and", "any", "are",
        "aren", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
        "but", "by", "can", "couldn", "couldn't", "d", "did", "didn", "didn't", "do", "does", "doesn",
        "doesn't", "doing", "don", "don't", "down", "during", "each", "few", "for", "from", "further",
        "had", "hadn", "hadn't", "has", "hasn", "hasn't", "have", "haven", "haven't", "having", "he",
        "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
        "isn", "isn't", "it", "it's", "its", "itself", "just", "ll", "m", "ma", "me", "mightn", "mightn't",
        "more", "most", "mustn", "mustn't", "my", "myself", "needn", "needn't", "no", "nor", "not", "now",
        "o", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over",
        "own", "re", "s", "same", "shan", "shan't", "she", "she's", "should", "should've", "shouldn",
        "shouldn't", "so", "some", "such", "t", "than", "that", "that'll", "the", "their", "theirs",
        "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too",
        "under", "until", "up", "ve", "very", "was", "wasn", "wasn't", "we", "were", "weren", "weren't",
        "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "won", "won't",
        "wouldn", "wouldn't", "y", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
        "yourself", "yourselves"
    }

    def _lemmatize_word(word: str) -> str:
        if len(word) > 4 and word.endswith("ies"):
            return word[:-3] + "y"
        if len(word) > 3 and word.endswith("es") and not word.endswith("fees"):
            return word[:-2]
        if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
            return word[:-1]
        return word


def clean_text(text: str) -> str:
    """Preprocess, clean, and tokenize text for intent classification."""
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\d+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))

    words = text.split()
    words = [w for w in words if w not in stop_words]
    words = [_lemmatize_word(w) for w in words]

    return " ".join(words)
