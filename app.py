from flask import Flask, request, send_file
from gtts import gTTS
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import os

app = Flask(__name__)

# این دو خط را برای هر زبان تغییر می‌دهی
LANG = "it"   # ← برای ایتالیا it ، برای فرانسه fr
ARTIST = "Italy News Today 🇮🇹"

@app.route("/tts", methods=["POST"])
def tts():
    data = request.json
    text = data.get("text", "")
    source = data.get("source", "")

    if not text:
        return {"error": "No text provided"}, 400

    filename = "tts_output.mp3"
    tmp_path = f"/tmp/{filename}"

    # تولید صدا
    tts = gTTS(text=text, lang=LANG)
    tts.save(tmp_path)

    # متادیتا
    try:
        audio = MP3(tmp_path, ID3=EasyID3)
    except:
        audio = MP3(tmp_path)
        audio.add_tags()

    audio["artist"] = ARTIST
    audio["title"] = text
    audio["album"] = f"Source: {source}"
    audio["genre"] = "News"
    audio.save()

    return send_file(tmp_path, mimetype="audio/mpeg", download_name=filename)

@app.route("/")
def home():

    return "TTS Server is running"
