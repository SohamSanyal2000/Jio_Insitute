import json
import nltk
import streamlit as st
from nltk import ngrams
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import CountVectorizer
import os

# File and directory information
list_of_unique_words_file_name = "List Of Unique Words.json"
script_directory = os.path.dirname(os.path.realpath(__file__))
list_of_unique_words_file_path = os.path.join(script_directory, list_of_unique_words_file_name)

# Load unique words from the JSON file
with open(list_of_unique_words_file_path, 'r') as file:
    unique_words = json.load(file)

# Preprocess data
unique_words = [word.lower() for word in unique_words]

# Create N-grams model
def generate_ngrams(words, n):
    return ngrams(words, n)

# Create bigrams
n = 2
ngram_model = generate_ngrams(unique_words, n)

# Train Word2Vec model
word2vec_model = Word2Vec(sentences=[unique_words], min_count=1, vector_size=100, window=5, sg=1)

# Define a function to suggest corrections for multiple words
def suggest_corrections(words, vocabulary, ngram_model, word2vec_model, max_distance=2):
    corrections = []

    for word in words:
        if word in vocabulary:
            corrections.append(word)
        else:
            # Check for partial matches using N-grams
            ngram_candidates = [w for w in vocabulary if word in w]
            if ngram_candidates:
                corrections.append(ngram_candidates[0])
            else:
                # Use Word2Vec to find similar words
                if word in word2vec_model.wv:
                    similar_words = word2vec_model.wv.most_similar(word)
                    if similar_words:
                        corrections.append(similar_words[0][0])
                    else:
                        corrections.append(word)
                else:
                    # Fallback to nltk edit distance for correction
                    candidate_corrections = [w for w in vocabulary if nltk.edit_distance(word, w) <= max_distance]
                    if candidate_corrections:
                        best_correction = min(candidate_corrections, key=lambda x: nltk.edit_distance(word, x))
                        corrections.append(best_correction)
                    else:
                        corrections.append(word)

    return corrections

# Streamlit UI
st.title("Spell Correction App")

# User input
user_input = st.text_input("Enter a sentence:")
user_words = user_input.split()

# Get corrections
corrections = suggest_corrections(user_words, unique_words, ngram_model, word2vec_model, max_distance=2)

# Display the corrections
st.write("Corrected sentence:", " ".join(corrections))
