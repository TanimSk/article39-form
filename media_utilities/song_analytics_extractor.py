import requests
from django.conf import settings

# Replace with your API key and the YouTube video ID
API_KEY = settings.YOUTUBE_API_KEY
VIDEO_ID = "VIDEO_ID_HERE"

# Define the endpoint and parameters
url = "https://www.googleapis.com/youtube/v3/videos"
params = {"part": "snippet,statistics,contentDetails", "id": VIDEO_ID, "key": API_KEY}

# Send the request
response = requests.get(url, params=params)

# Check if the response is successful
if response.status_code == 200:
    data = response.json()
    if data["items"]:
        video = data["items"][0]
        title = video["snippet"]["title"]
        stats = video["statistics"]
        details = video["contentDetails"]

        print(f"📹 Title: {title}")
        print(f"👍 Likes: {stats.get('likeCount', 'Hidden')}")
        print(f"💬 Comments: {stats.get('commentCount', 'Disabled')}")
        print(f"👁️ Views: {stats.get('viewCount', 'N/A')}")
        print(f"⏱️ Duration: {details['duration']}")
    else:
        print("❌ No video found with that ID.")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
