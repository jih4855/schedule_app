import os
import whisper
import datetime
import json
import glob
import yt_dlp
from rich.console import Console
import re

console = Console()

class Audio:
    def __init__(self, text_output="text", source_file="source_file"):
        self.text_output = text_output
        self.source_file = source_file


    #음성파일을 텍스트로 변환하기
    def transcribe_audio(self, whisper_model:str="large-v3", audio_extensions:list=["mp3","wav","m4a","flac","aac","ogg"]):
        from rich.progress import track 

        audio_file = []
        source_file = os.path.abspath(self.source_file)
        console.print(f"Source folder: {source_file}")

        # 텍스트 저장 폴더 만들기
        os.makedirs(self.text_output, exist_ok=True)

        if not os.path.isdir(source_file):
            console.print(f"소스 폴더가 없습니다: {source_file}")
            return

        try:
            # 패턴 정규화: ["*.mp3"]도, ["mp3"]도 모두 지원
            patterns = []
            for ext in audio_extensions:
                if any(ch in ext for ch in ("*", "?", "[")):  # 이미 패턴이면 그대로
                    patterns.append(ext)
                else:  # 확장자 형식이면 "*.ext"로 변환
                    patterns.append(f"*.{ext.lstrip('.')}")

            # 파일 수집
            for patt in track(patterns, description="🎵 음성파일 확인 중..."):
                audio_file.extend(glob.glob(os.path.join(source_file, patt)))

            # 중복 제거 + 정렬
            audio_file = sorted(set(audio_file))
            console.print(f"총 {len(audio_file)}개의 음성파일 발견")

            if not audio_file:
                console.print("No audio files found.")
                return

            # 실제 작업 직전에 모델 로드
            model = whisper.load_model(whisper_model)

            for audio in track(audio_file, description="🎵 음성파일 변환 중..."):
                json_filename = os.path.basename(audio) + ".json"
                json_path = os.path.join(self.text_output, json_filename)

                if os.path.exists(json_path):
                    console.print(f"이미 존재함: {json_filename} (건너뛰기)")
                    continue

                result = model.transcribe(audio)
                text = result.get("text", "")
                console.print(os.path.basename(audio))
                console.print(text)

                json_data = {
                    "file_name": os.path.basename(audio),
                    "text": text,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error: {e}")

    def download_youtube_audio(self, urls=None, preferred_codec="mp3", preferred_quality="192"):
        """YouTube 영상에서 음성만 추출"""
        # 저장 폴더 보장
        os.makedirs(self.source_file, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.source_file}/%(title)s.%(ext)s',
            'writeautomaticsub': False,
            'writesubtitles': False,
            'nooverwrites': True,  # ← 중복 방지
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': preferred_codec,
                'preferredquality': preferred_quality,
            }],
            'ignoreerrors': True
        }
        successful = []
        failed = []

        for url in urls:
            if not url:
                print("url이 필요합니다.")
                continue
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    print(f"YouTube 음성 다운로드 완료: {url}")
                    successful.append(url)
            except Exception as e:
                print(f"❌ 다운로드 실패: {url} - {e}")
                failed.append(url)

        print(f"📊 결과: 성공 {len(successful)}개, 실패 {len(failed)}개")
        return successful, failed

