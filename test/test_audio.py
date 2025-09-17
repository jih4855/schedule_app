#상위폴더 모듈임포트
import os
import glob
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.audio_tool import Audio



audio_test = Audio(
    text_output="test_text",
    source_file="test_audio",
    whisper_model="small",
    urls=[
        "https://youtu.be/8qZHnkMgR0g?si=ryplkrbPobUJsXPJ"  # Another Example YouTube URL
    ],
    preferred_codec="mp3",
    preferred_quality="192"
)

audio_test.download_youtube_audio()
audio_test.transcribe_audio()