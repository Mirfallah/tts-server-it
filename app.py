
from flask import Flask, request, send_file, jsonify
from gtts import gTTS
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import os
import tempfile

app = Flask(__name__)

LANG = "de"
ARTIST = "Germany News Today 🇩🇪"


@app.route("/", methods=["GET"])
def home():
    return "German TTS Server is running"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "language": LANG})


@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json(silent=True) or {}

    title = str(data.get("title", "")).strip()
    summary = str(data.get("summary", "")).strip()
    source = str(data.get("source", "")).strip()

    text = f"{title}. {summary}".strip()

    if not title and not summary:
        return jsonify({"error": "No text provided"}), 400

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".mp3", delete=False
        ) as tmp:
            tmp_path = tmp.name

        tts_audio = gTTS(text=text, lang=LANG)
        tts_audio.save(tmp_path)

        try:
            audio = MP3(tmp_path, ID3=EasyID3)
            audio["artist"] = ARTIST
            audio["title"] = title or "German News"
            audio["album"] = source or "German News"
            audio["genre"] = "News"
            audio.save()
        except Exception:
            app.logger.warning("Could not write MP3 metadata")

        return send_file(
            tmp_path,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="german_news.mp3"
        )

    except Exception as e:
        app.logger.exception("TTS generation failed")
        return jsonify({"error": "TTS generation failed"}), 500

    finally:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
