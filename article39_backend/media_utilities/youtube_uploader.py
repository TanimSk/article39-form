import threading
import requests
import ffmpeg
import tempfile
from io import BytesIO
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow, argparser
from googleapiclient.http import MediaFileUpload
from urllib.parse import urlencode, urlparse, parse_qs
import httplib2
import random
import time
import os
import sys
from utils import send_song_status_update
from pathlib import Path


class YouTubeVideoUploader(threading.Thread):
    BASE_DIR = Path(__file__).resolve().parent.parent
    CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "media_utilities/client_secret.json")
    YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
    MAX_RETRIES = 10
    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

    def __init__(
        self,
        description: str,
        tags: list,
        song_instance=None,
    ):
        super().__init__()
        self.image_url = song_instance.thumbnail_url if song_instance else None
        self.audio_url = song_instance.audio_url if song_instance else None
        self.title = song_instance.title if song_instance else None
        self.description = description
        self.tags = tags
        self.user_name = song_instance.artist.singer_musician_info.full_name_english
        self.status = song_instance.status
        self.email = song_instance.artist.artist.email
        self.instance = song_instance

    def run(self):
        try:

            # update the song instance to processing
            self.instance.upload_status = "PROCESSING"
            self.instance.save()

            image_data = self.download_to_memory(self.image_url)
            audio_data = self.download_to_memory(self.audio_url)
            print("[✓] Downloaded audio and image to memory")

            video_path = self.create_video_in_memory(image_data, audio_data)
            print(f"[✓] Video created: {video_path}")

            self.instance.upload_status = "UPLOADING"
            self.instance.save()

            self.upload_to_youtube(
                video_path=video_path,
                title=self.title,
                description=self.description,
                tags=self.tags,
            )

            os.remove(video_path)
        except Exception as e:
            print(f"[✗] Error: {e}")

    def download_to_memory(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)

    def create_video_in_memory(
        self, image_bytesio: BytesIO, audio_bytesio: BytesIO
    ) -> str:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as img_file:
            img_file.write(image_bytesio.read())
            image_path = img_file.name

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio_file:
            audio_file.write(audio_bytesio.read())
            audio_path = audio_file.name

        output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_path = output_file.name
        output_file.close()

        image_input = ffmpeg.input(image_path, loop=1, framerate=1)
        audio_input = ffmpeg.input(audio_path)

        # Apply scaling filter to ensure even dimensions
        image_input = image_input.filter("scale", "trunc(iw/2)*2", "trunc(ih/2)*2")

        (
            ffmpeg.output(
                image_input,
                audio_input,
                output_path,
                vcodec="libx264",
                acodec="aac",
                pix_fmt="yuv420p",
                shortest=None,
                preset="ultrafast"
            ).run(overwrite_output=True)
        )

        os.remove(image_path)
        os.remove(audio_path)

        return output_path

    def get_authenticated_service(self):
        flow = flow_from_clientsecrets(
            self.CLIENT_SECRETS_FILE, scope=self.YOUTUBE_UPLOAD_SCOPE
        )
        storage = Storage(
            os.path.join(
                self.BASE_DIR, "media_utilities/youtube_uploader.py-oauth2.json"
            )
        )
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, argparser.parse_args())

        return build(
            self.YOUTUBE_API_SERVICE_NAME,
            self.YOUTUBE_API_VERSION,
            http=credentials.authorize(httplib2.Http()),
        )

    def upload_to_youtube(
        self, video_path, title, description, tags, category_id="10", privacy="public"
    ):
        youtube = self.get_authenticated_service()

        body = dict(
            snippet=dict(
                title=title, description=description, tags=tags, categoryId=category_id
            ),
            status=dict(privacyStatus=privacy),
        )

        insert_request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True),
        )

        self.resumable_upload(insert_request)

    def resumable_upload(self, request):
        response = None
        error = None
        retry = 0

        while response is None:
            try:
                print("[⇪] Uploading...")
                status, response = request.next_chunk()
                if response is not None:
                    if "id" in response:
                        print(f"[✓] Video uploaded: https://youtu.be/{response['id']}")
                        send_song_status_update(
                            song_title=self.instance.title,
                            user_name=self.user_name,
                            status="APPROVED",
                            email=self.email,
                            youtube_link=f"https://youtu.be/{response['id']}",
                        )

                        # update the song instance with the youtube url
                        self.instance.upload_status = "UPLOADED"
                        self.instance.youtube_url = f"https://youtu.be/{response['id']}"
                        self.instance.youtube_video_id = response["id"]
                        self.instance.youtube_like_count = 0
                        self.instance.youtube_comment_count = 0
                        self.instance.youtube_view_count = 0
                        self.instance.save()

                    else:
                        sys.exit(f"[✗] Upload failed: {response}")
            except Exception as e:
                if isinstance(e, self.RETRIABLE_EXCEPTIONS) or (
                    hasattr(e, "resp") and e.resp.status in self.RETRIABLE_STATUS_CODES
                ):
                    error = f"[!] Retriable error: {str(e)}"
                else:
                    raise
            if error:
                print(error)
                retry += 1
                if retry > self.MAX_RETRIES:
                    sys.exit("[✗] Max retries reached. Aborting.")
                sleep = random.uniform(1, 2**retry)
                print(f"[⏳] Sleeping {sleep:.2f} seconds before retrying...")
                time.sleep(sleep)


# Example usage
if __name__ == "__main__":
    image_url = "https://transfer.ongshak.com/uploads/article39/a0e8ed6b-35bf-41bd-aa66-54e0c4dabf6c_15803682.png"
    audio_url = "https://transfer.ongshak.com/uploads/test/f2662291-9fcb-4bac-8968-13d96e66eb29_file_example_MP3_5MG.mp3"

    uploader = YouTubeVideoUploader(
        image_url, audio_url, "Test Title", "Test Description", ["test", "video"]
    )
    uploader.start()
    print("[→] Background upload started.")
