import pandas as pd
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from youtube_transcript_api import YouTubeTranscriptApi
from langdetect import detect
from googleapiclient.discovery import build
import torch
import re

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

state_dict = torch.load("model_state.pt", map_location=device)

model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)

# Load the state dictionary into the model
model.load_state_dict(state_dict)

model.to(device)  # Move the model to the correct device

# Load the tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

# Initialize the YouTube Data API client
youtube = build('youtube', 'v3', developerKey='AIzaSyD0o01imQSCtnPlvopheI7-_cHV-14hxwU')

# Function to get details
def get_details(url):
    video_id = url.split('v=')[-1]

    # Try to get the transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        transcript = ' '.join([x['text'] for x in transcript])
    except:
        transcript = 'none'

# Try to get the video details
    response = youtube.videos().list(part='snippet,contentDetails', id=video_id).execute()
    try:
        item = response['items'][0]
        try:
            title = item['snippet']['title']
            if detect(title) == 'en':
                titles = title
            else:
                titles = 'none'
        except:
            titles = 'none'
        try:
            description = item['snippet']['description']
            if detect(description) == 'en':
                descriptions = description
            else:
                descriptions = 'none'
        except:
            descriptions = 'none'
        try:
            tag = ','.join(item['snippet']['tags'])
            if detect(tag) == 'en':
                tags = tag
            else:
                tags = 'none'
        except:
            tags = 'none'
        try:
            durations = item['contentDetails']['duration']
        except:
            durations = 'none'
    except:
        titles = 'none'
        descriptions = 'none'
        tags = 'none'
        durations = 'none'

    return transcript, title, description, tags, durations

# Function to preprocess text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', '', text)
    return text

def score(links):
    scores=[]
    for url in links:
        transcript, title, description, tags, duration = get_details(url)

        # Preprocess all the features
        transcript = preprocess_text(transcript)
        title = preprocess_text(title)
        description = preprocess_text(description)
        tags = preprocess_text(tags)
        duration = preprocess_text(duration)

        # Combine all the features
        combined_features = f"{transcript} {title} {description} {tags} {duration}"

        model.eval()
        inputs = tokenizer([combined_features], return_tensors='pt', padding=True, truncation=True, max_length=512)
        inputs = inputs.to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim = 1)
        score = probabilities[0, 1].item()  # Probability of class P
        scores.append(score)
    return scores
