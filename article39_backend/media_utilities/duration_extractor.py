import requests
import ffmpeg
import tempfile
import os


def get_audio_duration_from_url(url):
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
            return None

        duration = float(audio_streams[0]["duration"])

        return duration

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
    except ffmpeg.Error as e:
        print(f"ffmpeg error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    finally:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)


# Example usage

if __name__ == "__main__":
    # Replace with your audio URL
    audio_url = "https://transfer.ongshak.com/uploads/article39/60357a70-24cf-4031-8529-58bf8ca0494d_Oktroy%20Mor%20Road.m4a"
    duration = get_audio_duration_from_url(audio_url)

    if duration is not None:
        print(f"The duration of the audio file is: {duration:.2f} seconds")
    else:
        print("Could not retrieve audio duration.")
