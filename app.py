"""
LessonCast - Local TTS Podcast Server
Model: Kokoro-TTS (https://github.com/hexgrad/kokoro)
Run: python app.py
"""

import multiprocessing
multiprocessing.freeze_support()

import os
import sys

if getattr(sys, 'frozen', False):
    os.environ['HF_HOME'] = os.path.join(sys._MEIPASS, 'kokoro_model')
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
import soundfile as sf
import numpy as np
import uuid
import json
import time

app = Flask(__name__)
CORS(app)

AUDIO_DIR = "audio_output"
os.makedirs(AUDIO_DIR, exist_ok=True)

# ─── Load Kokoro pipelines once at startup ──────────────────────────────────
print("⏳ Loading Kokoro TTS model (English)...")
try:
    from kokoro import KPipeline
    pipeline_en = KPipeline(lang_code='a')   # American English
    pipeline_gb = KPipeline(lang_code='b')   # British English
    print("✅ English pipeline loaded!")
    MODEL_LOADED = True
except Exception as e:
    print(f"❌ Failed to load Kokoro: {e}")
    pipeline_en = pipeline_gb = None
    MODEL_LOADED = False

print("⏳ Loading Kokoro TTS model (French)...")
try:
    pipeline_fr = KPipeline(lang_code='f')   # French
    print("✅ French pipeline loaded!")
    FR_LOADED = True
except Exception as e:
    print(f"⚠️  French pipeline failed (will still work for English): {e}")
    pipeline_fr = None
    FR_LOADED = False


def get_pipeline(voice_id):
    """Pick the right pipeline based on voice prefix."""
    if voice_id.startswith('ff_') or voice_id.startswith('fm_'):
        return pipeline_fr
    elif voice_id.startswith('bf_') or voice_id.startswith('bm_'):
        return pipeline_gb
    else:
        return pipeline_en


# Available Kokoro voices
VOICES = {
    # ── American English ──
    "af_heart":    {"name": "Heart",    "gender": "Female", "accent": "American", "lang": "EN"},
    "af_bella":    {"name": "Bella",    "gender": "Female", "accent": "American", "lang": "EN"},
    "af_nicole":   {"name": "Nicole",   "gender": "Female", "accent": "American", "lang": "EN"},
    "af_sarah":    {"name": "Sarah",    "gender": "Female", "accent": "American", "lang": "EN"},
    "af_sky":      {"name": "Sky",      "gender": "Female", "accent": "American", "lang": "EN"},
    "am_adam":     {"name": "Adam",     "gender": "Male",   "accent": "American", "lang": "EN"},
    "am_michael":  {"name": "Michael",  "gender": "Male",   "accent": "American", "lang": "EN"},
    # ── British English ──
    "bf_emma":     {"name": "Emma",     "gender": "Female", "accent": "British",  "lang": "EN"},
    "bf_isabella": {"name": "Isabella", "gender": "Female", "accent": "British",  "lang": "EN"},
    "bm_george":   {"name": "George",   "gender": "Male",   "accent": "British",  "lang": "EN"},
    "bm_lewis":    {"name": "Lewis",    "gender": "Male",   "accent": "British",  "lang": "EN"},
    # ── French ──
    "ff_siwis":    {"name": "Siwis",    "gender": "Female", "accent": "French",   "lang": "FR"},
}


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/voices", methods=["GET"])
def get_voices():
    return jsonify({"voices": VOICES, "model_loaded": MODEL_LOADED, "fr_loaded": FR_LOADED})


@app.route("/generate", methods=["POST"])
def generate():
    """Streaming generate via Server-Sent Events — sends progress as chunks arrive."""
    if not MODEL_LOADED:
        return jsonify({"error": "Kokoro model not loaded. Check console for details."}), 500

    data  = request.get_json(force=True)
    text  = data.get("text", "").strip()
    voice = data.get("voice", "af_heart")
    speed = float(data.get("speed", 1.0))

    if not text:
        return jsonify({"error": "No text provided"}), 400
    if len(text) > 500000:
        return jsonify({"error": "Text too long (max 500,000 characters)"}), 400

    job_id   = str(uuid.uuid4())[:8]
    out_path = os.path.join(AUDIO_DIR, f"{job_id}.wav")
    pipe     = get_pipeline(voice)

    def stream():
        if pipe is None:
            yield f"data: {json.dumps({'error': 'Pipeline not available for this voice'})}\n\n"
            return

        try:
            start        = time.time()
            audio_chunks = []
            total_chars  = len(text)
            chars_done   = 0

            gen = pipe(text, voice=voice, speed=speed)
            for graphemes, phonemes, audio in gen:
                if audio is not None:
                    audio_chunks.append(audio)

                if graphemes:
                    chars_done = min(chars_done + len(graphemes), total_chars)
                pct = round((chars_done / total_chars) * 95)
                secs_so_far = round(time.time() - start)
                yield f"data: {json.dumps({'pct': pct, 'elapsed': secs_so_far})}\n\n"

            if not audio_chunks:
                yield f"data: {json.dumps({'error': 'No audio generated'})}\n\n"
                return

            full_audio = np.concatenate(audio_chunks)
            sf.write(out_path, full_audio, 24000)

            elapsed  = round(time.time() - start, 1)
            duration = round(len(full_audio) / 24000, 1)
            print(f"✅ Generated {duration}s audio in {elapsed}s → {out_path}")

            yield f"data: {json.dumps({'pct': 100, 'done': True, 'audio_url': f'/audio/{job_id}.wav', 'duration': duration, 'elapsed': elapsed, 'job_id': job_id})}\n\n"

        except Exception as e:
            print(f"❌ Generation error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return app.response_class(stream(), mimetype="text/event-stream",
                              headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)


@app.route("/download/<filename>")
def download_audio(filename):
    """Force-download with a clean filename instead of a UUID."""
    safe = filename.replace("..", "").replace("/", "")
    return send_from_directory(
        AUDIO_DIR, safe,
        as_attachment=True,
        download_name=f"lessoncast_{safe}"
    )


@app.route("/status")
def status():
    return jsonify({
        "model": "Kokoro-TTS",
        "loaded": MODEL_LOADED,
        "voices": len(VOICES),
        "audio_files": len(os.listdir(AUDIO_DIR))
    })


if __name__ == "__main__":
    print("\n🎙️  LessonCast TTS Server")
    print("─" * 35)
    print("🌐  Open: http://localhost:5000")
    print("─" * 35 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)