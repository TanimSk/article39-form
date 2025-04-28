import requests
import ffmpeg
import tempfile
import os
import threading


def get_audio_duration_from_url(url, callback):
    try:
        # Download the audio file
        response = requests.get(url)
        response.raise_for_status()

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name

        # Probe using ffmpeg
        probe = ffmpeg.probe(tmp_path)
        audio_streams = [
            stream for stream in probe["streams"] if stream["codec_type"] == "audio"
        ]

        if not audio_streams:
            print("No audio stream found.")
            callback(None)
            return

        duration = int(float(audio_streams[0]["duration"]))

        print(f"Audio duration: {duration} seconds")
        callback(duration)

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        callback(None)
    except ffmpeg.Error as e:
        print(f"ffmpeg error: {e}")
        callback(None)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        callback(None)
    finally:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)


def get_audio_duration_from_url_threaded(url, callback):
    print("Starting thread to get audio duration...")
    thread = threading.Thread(target=get_audio_duration_from_url, args=(url, callback))
    thread.start()


# Example usage

if __name__ == "__main__":
    # Replace with your audio URL
    audio_url = "https://transfer.ongshak.com/uploads/article39/60357a70-24cf-4031-8529-58bf8ca0494d_Oktroy%20Mor%20Road.m4a"

    def print_duration(duration):
        if duration is not None:
            print(f"The duration of the audio file is: {duration:.2f} seconds")
        else:
            print("Could not retrieve audio duration.")

    get_audio_duration_from_url_threaded(audio_url, print_duration)
