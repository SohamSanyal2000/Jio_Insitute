from batch_loader import score
import math
from googleapiclient.discovery import build

def search_youtube(query, number_of_videos):
    youtube = build('youtube', 'v3', developerKey='AIzaSyD0o01imQSCtnPlvopheI7-_cHV-14hxwU')
    search_response = youtube.search().list(
        q=query,  
        part='snippet',
        maxResults=number_of_videos 
    ).execute()

    videos = []

    # Iterate over the search results
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            video_id = search_result['id']['videoId']
            video_response = youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()

            duration = video_response['items'][0]['contentDetails']['duration']
            formatted_duration = format_duration(duration)

            video_info = video_response['items'][0]

            videos.append({
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'title': video_info['snippet']['title'],
                'description': video_info['snippet']['description'],
                'publishedAt': video_info['snippet']['publishedAt'],
                'length': formatted_duration,
                'viewCount': video_info['statistics']['viewCount'],
                'likeCount': video_info['statistics'].get('likeCount', 0),
                'dislikeCount': video_info['statistics'].get('dislikeCount', 0),
                'commentCount': video_info['statistics'].get('commentCount', 0),
                'videoType': video_info['snippet']['liveBroadcastContent'],  # 'none', 'upcoming', or 'live'
            })

    return videos

def format_duration(duration):

    hours, minutes, seconds = 0, 0, 0
    time = duration[2:]  
    while time:
        value = ''
        while time[0].isdigit():
            value += time[0]
            time = time[1:]
        unit = time[0]
        time = time[1:]

        if unit == 'H':
            hours = int(value)
        elif unit == 'M':
            minutes = int(value)
        elif unit == 'S':
            seconds = int(value)
    formatted_duration = f"{hours} hours {minutes} minutes and {seconds} seconds" # Format the duration into a string

    return formatted_duration

def get_classifier_score(url_list): 
    results = score(url_list)
    return results

def get_youtube_score(total_results):
    yt_scores = [((total_results+1-yt_rank)/total_results) for yt_rank in range(1, total_results+1)]
    return yt_scores

def get_aggregated_score(videos, total_results):
    
    url_list = [video.get("url", "") for video in videos]
    classifier_scores = get_classifier_score(url_list)
    youtube_scores = get_youtube_score(total_results)

    for i in range(total_results):
        aggregated_score = (math.sqrt((classifier_scores[i])**2 + (youtube_scores[i])**2))/math.sqrt(2)
        scores_dict = {
            "classifier_score": classifier_scores[i],
            "youtube_score": youtube_scores[i],
            "aggregated_score": aggregated_score
        }

        videos[i].update(scores_dict)        
    return videos

def return_search_results_final(query, num_results):
    search_results = search_youtube(query, num_results)
    got_results = len(search_results)
    videos = get_aggregated_score(search_results, got_results)
    sorted_videos = sorted(videos, key=lambda x: x['aggregated_score'], reverse=True)
    return sorted_videos


def rerank_for_query(query, count):
    return return_search_results_final(query, count)
