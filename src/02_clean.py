"""cleans raw data & make clean dataset"""
import json
import re
from pathlib import Path

import pandas as pd
import nltk
import unicodedata
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from num2words import num2words

# --- Setup (run once) ---
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def remove_emojis(text):
    return ''.join(
        char for char in text
        if not unicodedata.category(char).startswith('So')
    )

def numbers_to_words(text):
    def replacer(match):
        try:
            return num2words(int(match.group()))
        except:
            return match.group()
    return re.sub(r'\d+', replacer, text)

def clean_text(text):
    if not isinstance(text, str):
        return ""

    # 1. lowercase FIRST
    text = text.lower()

    # 2. remove emojis (better method)
    text = remove_emojis(text)

    # 3. convert numbers BEFORE removing punctuation
    text = numbers_to_words(text)

    # 4. remove punctuation + special characters
    text = re.sub(r'[^a-z\s]', ' ', text)

    # 5. normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # 6. remove stopwords + lemmatize
    words = []
    for word in text.split():
        if word not in stop_words:
            lemma = lemmatizer.lemmatize(word)
            words.append(lemma)

    return " ".join(words)

# --- Load JSONL ---
project_root = Path(__file__).resolve().parent.parent
input_file = project_root / "data" / "reviews_raw.jsonl"
output_file = project_root / "data" / "reviews_clean.jsonl"

data = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        data.append(json.loads(line))

df = pd.DataFrame(data)

# --- Basic cleaning ---
df = df.dropna(subset=["content"])  # remove empty content

# remove extremely short reviews (before cleaning)
df = df[df["content"].str.strip().str.len() > 5]

# remove duplicates based on content
df = df.drop_duplicates(subset=["content"])

# --- Apply text cleaning ---
df["content"] = df["content"].apply(clean_text)

# remove empty results after cleaning
df = df[df["content"].str.strip().str.len() > 2]

# --- Save back to JSONL ---
with open(output_file, "w", encoding="utf-8") as f:
    for _, row in df.iterrows():
        record = row.to_dict()
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"Cleaning complete. Saved to {output_file}")