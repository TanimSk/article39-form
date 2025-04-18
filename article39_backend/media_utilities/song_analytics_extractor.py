import threading
import requests
from django.conf import settings
from dotenv import load_dotenv
from artist.models import Song
from django.db.models import QuerySet
import os

load_dotenv(".env")

class YouTubeVideoFetcher(threading.Thread):
    def __init__(self, song_instances: QuerySet[Song]):
        super().__init__()
        self.song_instances = song_instances
        self.api_key = os.getenv("YOUTUBE_API_KEY")

    def run(self):
        url = "https://www.googleapis.com/youtube/v3/videos"

        for song_instance in self.song_instances:
            params = {
                "part": "snippet,statistics,contentDetails",
                "id": song_instance.youtube_video_id,
                "key": self.api_key,
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                if data["items"]:
                    video = data["items"][0]
                    stats = video["statistics"]

                    song_instance.youtube_like_count = stats.get("likeCount", 0)
                    song_instance.youtube_comment_count = stats.get("commentCount", 0)
                    song_instance.youtube_view_count = stats.get("viewCount", 0)
                    song_instance.save()
                    print(f"✅ Updated {song_instance.title} with YouTube stats.")
                else:
                    print("❌ No video found with that ID.")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
