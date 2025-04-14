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

class YouTubeVideoUploader(threading.Thread):
    CLIENT_SECRETS_FILE = "./client_secret.json"
    YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
    MAX_RETRIES = 10
    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

    def __init__(self, image_url, audio_url, title, description, tags):
        super().__init__()
        self.image_url = image_url
        self.audio_url = audio_url
        self.title = title
        self.description = description
        self.tags = tags

    def run(self):
        try:
            image_data = self.download_to_memory(self.image_url)
            audio_data = self.download_to_memory(self.audio_url)
            print("[✓] Downloaded audio and image to memory")

            video_path = self.create_video_in_memory(image_data, audio_data)
            print(f"[✓] Video created: {video_path}")

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

    def create_video_in_memory(self, image_bytesio: BytesIO, audio_bytesio: BytesIO) -> str:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as img_file:
            img_file.write(image_bytesio.read())
            image_path = img_file.name

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio_file:
            audio_file.write(audio_bytesio.read())
            audio_path = audio_file.name

        output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_path = output_file.name
        output_file.close()

        image_input = ffmpeg.input(image_path, loop=1)
        audio_input = ffmpeg.input(audio_path)

        (
            ffmpeg.output(
                image_input,
                audio_input,
                output_path,
                vcodec="libx264",
                acodec="aac",
                pix_fmt="yuv420p",
                shortest=None,
            ).run(overwrite_output=True)
        )

        os.remove(image_path)
        os.remove(audio_path)

        return output_path

    def get_authenticated_service(self):
        flow = flow_from_clientsecrets(self.CLIENT_SECRETS_FILE, scope=self.YOUTUBE_UPLOAD_SCOPE)
        storage = Storage("%s-oauth2.json" % os.path.basename(__file__))
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, argparser.parse_args())

        return build(
            self.YOUTUBE_API_SERVICE_NAME,
            self.YOUTUBE_API_VERSION,
            http=credentials.authorize(httplib2.Http()),
        )

    def upload_to_youtube(self, video_path, title, description, tags, category_id="10", privacy="public"):
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


class SoundCloudUploader:
    def __init__(self, client_id, client_secret, redirect_uri="http://localhost:8080/callback"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None

    def authenticate(self):
        # Step 1: Generate the authorization URL
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': '*',
            'display': 'popup'
        }
        authorize_url = f"https://soundcloud.com/connect?{urlencode(params)}"

        print("\n🔗 Please open this URL in your browser and authorize the app:")
        print(authorize_url)

        # Step 2: Prompt for redirected URL
        redirected_url = input("\n🔁 After authorization, paste the full redirected URL here:\n> ")

        # Step 3: Extract the 'code' from the URL
        parsed_url = urlparse(redirected_url)
        code = parse_qs(parsed_url.query).get("code")
        if not code:
            print("❌ No code found in the URL.")
            return
        code = code[0]

        # Step 4: Exchange code for access token
        token_url = "https://api.soundcloud.com/oauth2/token"
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
            'code': code
        }

        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        self.access_token = response.json()['access_token']
        print("✅ Access token received!")

    def upload_track(self, file_path, title="Untitled Track", sharing="public"):
        if not self.access_token:
            print("❌ Please authenticate first.")
            return

        def upload():
            print(f"\n🚀 Uploading '{title}'...")
            url = "https://api.soundcloud.com/tracks"
            headers = {'Authorization': f'OAuth {self.access_token}'}
            files = {
                'track[title]': (None, title),
                'track[asset_data]': open(file_path, 'rb'),
                'track[sharing]': (None, sharing),
            }

            response = requests.post(url, headers=headers, files=files)
            if response.status_code == 201:
                track_url = response.json().get('permalink_url')
                print(f"✅ Upload successful: {track_url}")
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")

        thread = threading.Thread(target=upload)
        thread.start()


# Example usage
if __name__ == "__main__":
    image_url = "https://transfer.ongshak.com/uploads/article39/a0e8ed6b-35bf-41bd-aa66-54e0c4dabf6c_15803682.png"
    audio_url = "https://transfer.ongshak.com/uploads/test/f2662291-9fcb-4bac-8968-13d96e66eb29_file_example_MP3_5MG.mp3"

    uploader = YouTubeVideoUploader(image_url, audio_url, "Test Title", "Test Description", ["test", "video"])
    uploader.start()
    print("[→] Background upload started.")