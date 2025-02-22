# LSTM Model Training File

import json
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt

# Input file name and path setup
input_file_name = "Extracted Features.json"
script_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_directory, input_file_name)

# Function to extract library titles from a JSON file
def get_library_titles_from_json(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        titles = [library['title'] for library in data]
    return titles

# Get library titles from the JSON file
library_titles = get_library_titles_from_json(file_path)

# Tokenization of library titles
tokenizer = Tokenizer()
tokenizer.fit_on_texts(library_titles)
total_words = len(tokenizer.word_index) + 1

# Generate input sequences for training
input_sequences = []
for title in library_titles:
    token_list = tokenizer.texts_to_sequences([title])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

# Pad sequences to have consistent length
max_sequence_length = max([len(seq) for seq in input_sequences])
input_sequences = pad_sequences(input_sequences, maxlen=max_sequence_length, padding='pre')

# Prepare input (X) and output (y) for training
X, y = input_sequences[:, :-1], input_sequences[:, -1]
y = to_categorical(y, num_classes=total_words)

# Model Architecture
model = Sequential()
model.add(Embedding(total_words, 50, input_length=max_sequence_length-1))
model.add(LSTM(100))
model.add(Dense(total_words, activation='softmax'))

# Model Compilation and Training
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
history = model.fit(X, y, epochs=5, verbose=1)

# Save the trained model to a file
output_file_name = "LSTM model.h5"
output_file_path = os.path.join(script_directory, output_file_name)
model.save(output_file_path)

# Function to plot the learning curve (loss over epochs)
def plot_learning_curve(history):
    loss = history.history['loss']
    epochs = [i for i, _ in enumerate(loss)]
    plt.scatter(epochs, loss, color='skyblue', marker='o')  # Use marker='o' for dots
    plt.title('Model Loss Over Epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.show()

# Plot the learning curve using the training history
plot_learning_curve(history)
