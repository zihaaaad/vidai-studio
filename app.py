"""
VidAI Studio — Backend
Converts video audio into AI-generated content using Google Gemini.
Also supports direct video/audio download.
"""

import os
import sys
import json
import time
import uuid
import re
import logging
import webbrowser
import threading

import yt_dlp
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("studio")

# ──────────────────────────────────────────────
# App Setup
# ──────────────────────────────────────────────
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
TEMP_DIR = os.path.join(BASE_DIR, "tmp")
MAX_AUDIO_SIZE_MB = 20
MAX_HISTORY_ITEMS = 50

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

AVAILABLE_MODELS = [
    {"id": "gemini-1.5-flash",      "name": "Gemini 1.5 Flash",      "desc": "Fast & cost-efficient"},
    {"id": "gemini-1.5-pro",        "name": "Gemini 1.5 Pro",        "desc": "High quality, complex tasks"},
    {"id": "gemini-2.0-flash-exp",  "name": "Gemini 2.0 Flash (Exp)", "desc": "Next-gen speed & intelligence"},
    {"id": "gemini-pro",            "name": "Gemini 1.0 Pro",        "desc": "Standard legacy model"},
]

# Thread-safe job tracking
_jobs: dict = {}
_jobs_lock = threading.Lock()

# ──────────────────────────────────────────────
# Utility functions
# ──────────────────────────────────────────────

def _load_json(path, default):
    """Load a JSON file, returning *default* on any error."""
    if not os.path.exists(path):
        return default() if callable(default) else default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        log.warning("Could not read %s, using default", path)
        return default() if callable(default) else default


def _save_json(path, data):
    """Atomically write JSON to *path*."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def load_config() -> dict:
    return _load_json(CONFIG_FILE, dict)


def save_config(patch: dict):
    cfg = load_config()
    cfg.update(patch)
    _save_json(CONFIG_FILE, cfg)


def load_history() -> list:
    return _load_json(HISTORY_FILE, list)


def save_history_entry(entry: dict):
    history = load_history()
    history.insert(0, entry)
    _save_json(HISTORY_FILE, history[:MAX_HISTORY_ITEMS])


def detect_platform(url: str) -> str:
    """Return a platform name from the URL domain."""
    url = url.lower()
    for domain, name in [
        ("facebook.com", "facebook"), ("fb.watch", "facebook"), ("fb.com", "facebook"),
        ("youtube.com", "youtube"),   ("youtu.be", "youtube"),
        ("instagram.com", "instagram"),
        ("tiktok.com", "tiktok"),
        ("twitter.com", "twitter"),   ("x.com", "twitter"),
    ]:
        if domain in url:
            return name
    return "other"


_URL_RE = re.compile(
    r"^https?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

def validate_url(url: str) -> bool:
    return bool(_URL_RE.match(url))


def parse_api_error(exc, model_id: str) -> str:
    """Convert a raw Gemini exception into a short, user-friendly string."""
    text = str(exc)

    if "429" in text or "quota" in text.lower():
        m = re.search(r"retry[_ ]?(?:in|delay)?[:\s]*(\d+)", text, re.IGNORECASE)
        wait = m.group(1) if m else "60"
        return f"Rate limit reached for {model_id}. Wait ~{wait}s or switch model."

    if "401" in text or "api_key" in text.lower():
        return "Invalid API Key. Check your key in Settings."

    if "403" in text or "permission" in text.lower():
        return "Permission denied. Your API key may not have access to this model."

    if "404" in text or "not found" in text.lower():
        return f"Model '{model_id}' not found. Select a different model."

    if "safety" in text.lower() or "blocked" in text.lower():
        return "Content blocked by safety filters. Try a different video."

    return text[:200] if len(text) > 200 else text


def resource_path(relative_path: str) -> str:
    """Resolve resource path for both dev and PyInstaller builds."""
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, relative_path)


# ──────────────────────────────────────────────
# Core processing (runs in background thread)
# ──────────────────────────────────────────────

def _update_job(job_id: str, **fields):
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].update(fields)


def _process_video(job_id, video_url, lang, style, api_key, model_id, custom_instruction):
    """Download audio → upload to Gemini → generate content. Called in a daemon thread."""
    audio_path = None
    try:
        # Step 1 — Download audio
        _update_job(job_id, step="downloading", progress=10,
                    message="Downloading audio from video...")
        log.info("[%s] Downloading %s", job_id, video_url)

        ts = int(time.time())
        out_template = os.path.join(TEMP_DIR, f"audio_{ts}")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": out_template,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }],
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_title = info.get("title", "Untitled")

        audio_path = out_template + ".mp3"

        if not os.path.exists(audio_path):
            _update_job(job_id, status="error", step="failed", progress=0,
                        error="Could not download audio. Check if the video is public.")
            return

        size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        if size_mb > MAX_AUDIO_SIZE_MB:
            _update_job(job_id, status="error", step="failed", progress=0,
                        error=f"Audio too large ({size_mb:.1f} MB). Max {MAX_AUDIO_SIZE_MB} MB.")
            return

        # Step 2 — Upload to Gemini
        _update_job(job_id, progress=30, step="uploading",
                    message="Uploading audio to AI engine...")
        log.info("[%s] Uploading %.1f MB", job_id, size_mb)

        genai.configure(api_key=api_key)
        uploaded = genai.upload_file(path=audio_path)

        _update_job(job_id, progress=50, step="processing",
                    message="AI is analyzing the audio...")

        while uploaded.state.name == "PROCESSING":
            time.sleep(1)
            uploaded = genai.get_file(uploaded.name)

        if uploaded.state.name == "FAILED":
            _update_job(job_id, status="error", step="failed", progress=0,
                        error="AI failed to process the audio file.")
            return

        # Step 3 — Generate content
        _update_job(job_id, progress=70, step="generating",
                    message="Generating content with AI...")
        log.info("[%s] Generating (%s, %s, %s)", job_id, model_id, style, lang)

        system_prompt = (
            f"Role: Expert Content Editor and Writer.\n"
            f"Task: Analyze the audio carefully and create a '{style}'.\n"
            f"Language: Output strictly in {lang}.\n"
            f"Style Guide:\n"
            f"- Use clean, professional formatting with Markdown.\n"
            f"- Use bold headers (##) for sections.\n"
            f"- Use bullet points for key takeaways.\n"
            f"- Write in a natural, professional tone.\n"
            f"- If the language is Bengali, use natural Bengali phrasing."
        )

        if custom_instruction and custom_instruction.strip():
            prompt = f"{system_prompt}\n\nAdditional User Instructions:\n{custom_instruction.strip()}"
        else:
            prompt = system_prompt

        valid_ids = [m["id"] for m in AVAILABLE_MODELS]
        if model_id not in valid_ids:
            model_id = "gemini-1.5-flash"

        try:
            model = genai.GenerativeModel(model_id)
            response = model.generate_content([prompt, uploaded])
            result_text = response.text
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                log.warning("[%s] Model %s not found, falling back to gemini-pro", job_id, model_id)
                _update_job(job_id, message="Model unavailable, trying fallback (Gemini 1.0 Pro)...")
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content([prompt, uploaded])
                result_text = response.text
                model_id = "gemini-pro (fallback)"
            else:
                raise e

        # Step 4 — Done
        _update_job(job_id, status="done", step="done", progress=100,
                    message="Content generated successfully!",
                    result=result_text, video_title=video_title)
        log.info("[%s] Done — %d words", job_id, len(result_text.split()))

        save_history_entry({
            "id": job_id,
            "url": video_url,
            "platform": detect_platform(video_url),
            "video_title": video_title,
            "model": model_id,
            "lang": lang,
            "style": style,
            "result": result_text,
            "word_count": len(result_text.split()),
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as exc:
        log.exception("[%s] Processing failed", job_id)
        _update_job(job_id, status="error", step="failed", progress=0,
                    error=parse_api_error(exc, model_id))
    finally:
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError:
                log.warning("Could not remove temp file %s", audio_path)


# ──────────────────────────────────────────────
# Download worker (video/audio without AI)
# ──────────────────────────────────────────────

def _download_media(job_id, video_url, fmt):
    """Download video or audio file. fmt = 'video' | 'audio'."""
    try:
        _update_job(job_id, step="downloading", progress=20,
                    message=f"Downloading {fmt} from video...")
        log.info("[%s] Downloading %s as %s", job_id, video_url[:60], fmt)

        ts = int(time.time())

        if fmt == "audio":
            ext = "mp3"
            out_template = os.path.join(TEMP_DIR, f"dl_{ts}")
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": out_template,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "quiet": True,
                "no_warnings": True,
            }
            expected_path = out_template + ".mp3"
        else:
            ext = "mp4"
            out_template = os.path.join(TEMP_DIR, f"dl_{ts}.%(ext)s")
            ydl_opts = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "outtmpl": out_template,
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
            }
            expected_path = None  # will find after download

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_title = info.get("title", "download")

        # Find the downloaded file
        if fmt == "audio":
            dl_path = expected_path
        else:
            # yt-dlp fills in the extension
            import glob
            candidates = glob.glob(os.path.join(TEMP_DIR, f"dl_{ts}.*"))
            dl_path = candidates[0] if candidates else None
            if dl_path:
                ext = os.path.splitext(dl_path)[1].lstrip(".")

        if not dl_path or not os.path.exists(dl_path):
            _update_job(job_id, status="error", step="failed", progress=0,
                        error="Download failed. The video may be private or unavailable.")
            return

        size_mb = os.path.getsize(dl_path) / (1024 * 1024)
        safe_title = re.sub(r'[^\w\s\-]', '', video_title).strip()[:60] or "download"
        filename = f"{safe_title}.{ext}"

        _update_job(job_id, status="done", step="done", progress=100,
                    message=f"{fmt.capitalize()} ready to download ({size_mb:.1f} MB)",
                    video_title=video_title,
                    download_path=dl_path,
                    download_filename=filename,
                    download_size_mb=round(size_mb, 1))
        log.info("[%s] Download ready: %s (%.1f MB)", job_id, filename, size_mb)

    except Exception as exc:
        log.exception("[%s] Download failed", job_id)
        _update_job(job_id, status="error", step="failed", progress=0,
                    error=f"Download failed: {str(exc)[:150]}")


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# — Config —

@app.route("/api/config", methods=["GET"])
def get_config():
    cfg = load_config()
    return jsonify({
        "api_key":       cfg.get("api_key", ""),
        "default_model": cfg.get("default_model", "gemini-2.0-flash"),
        "default_lang":  cfg.get("default_lang", "Bengali"),
        "default_style": cfg.get("default_style", "Summary"),
    })


@app.route("/api/config", methods=["POST"])
def post_config():
    data = request.json or {}
    if "api_key" in data and not data["api_key"].strip():
        return jsonify({"success": False, "error": "API Key cannot be empty."}), 400
    save_config(data)
    return jsonify({"success": True})


# — Models —

@app.route("/api/models", methods=["GET"])
def get_models():
    return jsonify({"models": AVAILABLE_MODELS})


# — Generate (async) —

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json or {}
    cfg = load_config()
    api_key = cfg.get("api_key")

    if not api_key:
        return jsonify({"success": False, "error": "API Key not set. Open Settings."}), 401

    url = data.get("url", "").strip()
    lang = data.get("lang", "Bengali")
    style = data.get("style", "Summary")
    model_id = data.get("model", cfg.get("default_model", "gemini-2.0-flash"))
    custom_instruction = data.get("custom_instruction", "")

    if not url:
        return jsonify({"success": False, "error": "URL is required."}), 400
    if not validate_url(url):
        return jsonify({"success": False, "error": "Invalid URL format."}), 400

    job_id = uuid.uuid4().hex[:8]
    with _jobs_lock:
        _jobs[job_id] = {
            "status": "running",
            "step": "queued",
            "progress": 0,
            "message": "Starting…",
            "result": None,
            "error": None,
            "video_title": None,
            "url": url,
            "platform": detect_platform(url),
        }

    thread = threading.Thread(
        target=_process_video,
        args=(job_id, url, lang, style, api_key, model_id, custom_instruction),
        daemon=True,
    )
    thread.start()
    log.info("Job %s started for %s", job_id, url[:60])

    # Remember user preferences
    save_config({"default_model": model_id, "default_lang": lang, "default_style": style})

    return jsonify({"success": True, "job_id": job_id})


# — Job status (polling) —

@app.route("/api/status/<job_id>", methods=["GET"])
def job_status(job_id):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found."}), 404
    return jsonify(job)


# — History —

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify({"history": load_history()})


@app.route("/api/history/<item_id>", methods=["DELETE"])
def delete_history_item(item_id):
    history = [h for h in load_history() if h.get("id") != item_id]
    _save_json(HISTORY_FILE, history)
    return jsonify({"success": True})


@app.route("/api/history", methods=["DELETE"])
def clear_history():
    _save_json(HISTORY_FILE, [])
    return jsonify({"success": True})


# — Download (video/audio) —

@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.json or {}
    url = data.get("url", "").strip()
    fmt = data.get("format", "video")  # 'video' or 'audio'

    if not url:
        return jsonify({"success": False, "error": "URL is required."}), 400
    if not validate_url(url):
        return jsonify({"success": False, "error": "Invalid URL format."}), 400
    if fmt not in ("video", "audio"):
        return jsonify({"success": False, "error": "Format must be 'video' or 'audio'."}), 400

    job_id = uuid.uuid4().hex[:8]
    with _jobs_lock:
        _jobs[job_id] = {
            "status": "running",
            "step": "queued",
            "progress": 0,
            "message": "Starting download…",
            "result": None,
            "error": None,
            "video_title": None,
            "url": url,
            "platform": detect_platform(url),
            "download_path": None,
            "download_filename": None,
            "download_size_mb": None,
        }

    thread = threading.Thread(
        target=_download_media,
        args=(job_id, url, fmt),
        daemon=True,
    )
    thread.start()
    log.info("Download job %s started (%s) for %s", job_id, fmt, url[:60])

    return jsonify({"success": True, "job_id": job_id})


@app.route("/api/download/file/<job_id>", methods=["GET"])
def serve_download(job_id):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found."}), 404
    if job.get("status") != "done" or not job.get("download_path"):
        return jsonify({"error": "File not ready."}), 400

    path = job["download_path"]
    name = job.get("download_filename", "download")

    if not os.path.exists(path):
        return jsonify({"error": "File expired. Please download again."}), 410

    return send_file(path, as_attachment=True, download_name=name)


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def _open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Timer(1.0, _open_browser).start()
    log.info("Starting FB AI Studio on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
