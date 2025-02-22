# Import necessary libraries
import json
import nltk
import re
import string
import os
import spacy
from nltk import ngrams
from PIL import Image
import streamlit as st
import numpy as np
import urllib.parse
from gensim.models import Word2Vec
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Define file names for model, features, and list of unique words
model_file_name = "LSTM model.h5"
features_file_name = "Extracted Features.json"
list_of_unique_words_file_name = "List Of Unique Words.json"

# Get the script directory
script_directory = os.path.dirname(os.path.realpath(__file__))

# Create file paths using the script directory and file names
model_file_path = os.path.join(script_directory, model_file_name)
features_file_path = os.path.join(script_directory, features_file_name)
list_of_unique_words_file_path = os.path.join(script_directory, list_of_unique_words_file_name)

# Load the trained LSTM model
model = load_model(model_file_path)

# Load unique words from a file and convert them to lowercase
with open(list_of_unique_words_file_path, 'r') as file:
    unique_words = json.load(file)
unique_words = [word.lower() for word in unique_words]

# ====================================== Spellcheck parts ========================================

# Function to generate n-grams from a list of words
def generate_ngrams(words, n):
    return ngrams(words, n)

# Set n for n-grams
n = 2
# Generate n-grams model from the list of unique words
ngram_model = generate_ngrams(unique_words, n)

# Create a Word2Vec model from the list of unique words
word2vec_model = Word2Vec(sentences=[unique_words], min_count=1, vector_size=100, window=5, sg=1)

# Function to suggest corrections for a list of words
def suggest_corrections(words, vocabulary, ngram_model, word2vec_model, max_distance=2):
    corrections = []

    for word in words:
        # If the word is already in the vocabulary, consider it correct
        if word in vocabulary:
            corrections.append(word)
        else:
            # Check if the word is part of any n-gram in the vocabulary
            ngram_candidates = [w for w in vocabulary if word in w]
            if ngram_candidates:
                corrections.append(ngram_candidates[0])
            else:
                # Check if the word is in the Word2Vec model
                if word in word2vec_model.wv:
                    similar_words = word2vec_model.wv.most_similar(word)
                    if similar_words:
                        corrections.append(similar_words[0][0])
                    else:
                        corrections.append(word)
                else:
                    # If the word is not in Word2Vec, perform spell correction using edit distance
                    candidate_corrections = [w for w in vocabulary if nltk.edit_distance(word, w) <= max_distance]
                    if candidate_corrections:
                        best_correction = min(candidate_corrections, key=lambda x: nltk.edit_distance(word, x))
                        corrections.append(best_correction)
                    else:
                        # If no corrections are found, keep the original word
                        corrections.append(word)

    return corrections

# ====================================== Spellcheck parts ========================================

# Function to retrieve product data from a JSON file
def get_product_data_from_json(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

# Load product data from the features file
product_data = get_product_data_from_json(features_file_path)

# Extract product names from the product data
product_names = [item['title'] for item in product_data]

# Tokenize product names using Keras Tokenizer
tokenizer = Tokenizer()
tokenizer.fit_on_texts(product_names)

# Create input sequences for LSTM training
input_sequences = []
for line in product_names:
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

# Determine the maximum sequence length for padding
max_sequence_length = max([len(seq) for seq in input_sequences])

# Function to generate suggestions using the LSTM model
def generate_suggestions(partial_input, model, tokenizer, max_sequence_length, num_suggestions=3):
    token_list = tokenizer.texts_to_sequences([partial_input])[0]
    token_list = pad_sequences([token_list], maxlen=max_sequence_length-1, padding='pre')
    predicted_probs = model.predict(token_list, verbose=0)[0]
    
    # Get the top N predicted indices
    top_indices = predicted_probs.argsort()[-num_suggestions:][::-1]
    
    # Convert indices back to words
    suggestions = [word for word, index in tokenizer.word_index.items() if index in top_indices]
    
    return suggestions

# Function to generate suggestions using the LSTM model and feed suggestions back to the model once.

# def generate_suggestions(partial_input, model, tokenizer, max_sequence_length, num_suggestions=2, iterations=2):
#     all_suggestions = []
    
#     for _ in range(iterations):
#         token_list = tokenizer.texts_to_sequences([partial_input])[0]
#         token_list = pad_sequences([token_list], maxlen=max_sequence_length-1, padding='pre')
#         predicted_probs = model.predict(token_list, verbose=0)[0]
        
#         # Get the top N predicted indices
#         top_indices = predicted_probs.argsort()[-num_suggestions:][::-1]
        
#         # Convert indices back to words
#         suggestions = [word for word, index in tokenizer.word_index.items() if index in top_indices]
        
#         # Append the suggestions to the seed for the next iteration
#         partial_input += " " + " ".join(suggestions)
        
#         all_suggestions.extend(suggestions)
    
#     return all_suggestions

# Function to retrieve matching products based on suggestions and seed input


#semantic search function 
# Load a different pre-trained word embeddings model

import spacy
import numpy as np

# Load the spaCy model with medium-sized English word vectors
nlp = spacy.load("en_core_web_md")

# Extract unique categories from the product data
unique_categories = list(set(item["category"] for item in product_data))

# Tokenize and convert categories to lowercase to create a list of all words
all_words = [word.lower() for category in unique_categories for word in category.split()]

# Create a list of unique words from the tokenized categories
unique_words_semantic = list(set(all_words))

def semantic_search(query, categories, threshold=0.6, top_n=6):
    """Perform semantic search by comparing vector representations of the query with
    vector representations of categories.

    Arguments - 
    - query (str): The search query.
    - categories (list): List of categories to compare with.
    - threshold (float): Similarity threshold for considering a match.

    Returns:
    - list: Sorted list of suggestions based on similarity scores."""

    # Get the vector representation of the search query
    query_embedding = nlp(query).vector

    # Store suggestions with their similarity scores
    suggestions = {}
    
    # Compare the query vector with each category vector
    for category in categories:
        category_embedding = nlp(category).vector
        similarity = np.dot(query_embedding, category_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(category_embedding))

        # Check if the similarity score is above the threshold
        if similarity > threshold:
            suggestions[category] = similarity

    # Sort suggestions by similarity score in descending order and return the top matches
    sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return sorted_suggestions

def retrieve_matching_products(seed, suggestions, product_catalog, max_results=5):
    """Retrieve products that match the search seed and suggestions from the product catalog.

    Args:
    - seed (str): The search seed.
    - suggestions (list): List of search suggestions.
    - product_catalog (list): List of products to search within.
    - max_results (int): Maximum number of matching products to retrieve.

    Returns:
    - list or None: List of matching products or None if no matches are found."""

    matching_products = []

    # Iterate through each product in the catalog
    for product in product_catalog:
        # Get the product title from the dictionary and convert to lowercase
        product_title = product.get('title', '').lower()

        # Check if at least one suggestion is present in the product title
        if any(suggestion.lower() in product_title for suggestion in suggestions):
            # Check if all words in the split seed are present in the product title as parts of words
            if all(word.lower() in product_title.split() for word in seed.split()):
                matching_products.append(product)

                # If max_results is specified and reached, break the loop
                if max_results is not None and len(matching_products) == max_results:
                    break

    # Return matching products or None if no matches are found
    return matching_products if matching_products else None

#generating the html link using the query terms
def generate_search_link(keyword_tuple):
    keyword = keyword_tuple[0]
    base_url = "https://www.gofynd.com/products/?q="
    encoded_keyword = "%20".join(keyword.split())
    return f"{base_url}{encoded_keyword}"


# Streamlit App
st.title("LSTM Product Search App")

# User input
user_input = st.text_input("", "")

# ====================================== Spellcheck parts ========================================

# Split user input into words
user_words = user_input.split()
# Perform spellchecking and obtain corrected sentence
corrections = suggest_corrections(user_words, unique_words, ngram_model, word2vec_model, max_distance=2)
corrected_sentence = " ".join(corrections)

# Check if the spell-corrected version is the same as the user input without special characters
if ''.join(c for c in user_input if c not in string.punctuation) == ''.join(c for c in corrected_sentence if c not in string.punctuation):
    corrected_sentence = user_input
else:
    st.write("Showing results for:", corrected_sentence)

# ====================================== Spellcheck parts ========================================
list_of_semantically_related_words = semantic_search(corrected_sentence, unique_words_semantic)    # <====================================== semantic search ========================================

# Generate suggestions (limit to top 5)
suggestions = generate_suggestions(corrected_sentence, model, tokenizer, max_sequence_length, num_suggestions=5)

st.write("Suggestions:", ", ".join(suggestions))

# Retrieve matching products
matching_products = retrieve_matching_products(corrected_sentence, suggestions, product_data)

# Check if matching_products is not None before iterating
if matching_products is not None:
    # Display products
    st.header("Matching Products")
    for product in matching_products:
        title = product['title']
        media_url = product['media']
        product_url = product['url']
        category = product['category']  # Extract category

        # Display product title with thumbnail and a link in two columns
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(media_url, width=50)
        with col2:
            st.markdown(f"<a href='{product_url}' style='color: white; text-decoration: none;font-size:20px;'>{title}</a>", unsafe_allow_html=True)

    # Display categories and links
    st.header("Categories")
    displayed_categories = set()  # Keep track of displayed categories
    for product in matching_products:
        category_name = product['category']
        category_url = product.get('category_url', '')  # Extract category URL

        # Check if the category has already been displayed
        if category_name not in displayed_categories:
            # Display category as link
            st.markdown(f"<a href='{category_url}' style='color: white; text-decoration: none;font-size:20px;'>{category_name}</a>", unsafe_allow_html=True)
            
            # Add the category to the set of displayed categories
            displayed_categories.add(category_name)

    # Display other relevant products section
    st.header("Similar Categories")

    # Generate and display links for each word in the list
    items_list = ",  ".join([f"<a href='{generate_search_link(items)}' style='color: white; text-decoration: none;font-size:20px;'>{items[0]}</a>" for items in list_of_semantically_related_words])
    st.markdown(items_list, unsafe_allow_html=True)

# Streamlit layout for about the app section
st.markdown("\n\n")
st.markdown("\n\n")
st.markdown("\n\n")
st.markdown("\n\n")

# About the App Section
# About the App Section
if st.button("About App"):
    st.title("About App")
    st.write("This Streamlit app features an LSTM-based autosuggest mechanism for an e-commerce catalog. The application aims to provide an interactive and user-friendly product search experience.")
    
    st.write("## Libraries Used:")
    st.write("1. **Streamlit:** The primary framework for building the web application, offering an interactive and user-friendly interface.")
    st.write("2. **TensorFlow and Keras:** Used for training and loading the LSTM model that powers the product search functionality.")
    st.write("3. **PIL (Pillow):** Used for handling images in the app.")
    st.write("4. **JSON:** The product catalog data is loaded from a JSON file.")
    st.write("5. **NLTK:** Natural Language Toolkit used for natural language processing tasks, including spell checking.")
    st.write("6. **Gensim:** Utilized for the Word2Vec model to suggest corrections for misspelled words.")
    st.write("7. **spaCy:** A natural language processing library employed for semantic search.")
    
    st.write("## About the Functioning:")
    st.write("1. **Product Search:** Users can enter a search term, and the app suggests relevant products based on the input using a trained LSTM model.")
    st.write("2. **Spellcheck Feature:** The app includes a spellcheck feature that suggests corrections for misspelled words using NLTK, Gensim, and scikit-learn.")
    st.write("3. **Matching Products:** The app displays matching products along with their titles, thumbnails, and links.")
    st.write("4. **Categories:** Matching products are categorized, and users can explore categories with clickable links.")
    st.write("5. **Data Loading:** Product data is loaded from a JSON file, and the LSTM model is used to generate suggestions.")
    st.write("6. **Semantic Search:** Utilizes spaCy for semantic search, finding semantically related words based on vector embeddings.")
    st.write("7. **Web Link Generation:** Clickable links are generated for product titles, categories, and other relevant products.")
    

