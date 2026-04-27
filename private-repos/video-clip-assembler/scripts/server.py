"""
HTTP server for Video Clip Assembler.
Uses http.server (stdlib) — no Flask needed.
"""

import hashlib
import hmac
import json
import os
import secrets
import sys
import threading
import time
import uuid
import tempfile
import shutil
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

# Add scripts dir to path
SCRIPTS_DIR = Path(__file__).parent
SKILL_DIR = SCRIPTS_DIR.parent
STATIC_DIR = SKILL_DIR / "static"
_DATA_ROOT_M1 = Path("/data") if os.path.isdir("/data") else SKILL_DIR
TEMP_DIR = _DATA_ROOT_M1 / "temp"
CLIPS_DIR = TEMP_DIR / "clips"

sys.path.insert(0, str(SCRIPTS_DIR))

from transcriber import transcribe_video
from translator import translate_sentences, match_keywords
from video_processor import build_video_phase1, build_video_phase2_subtitle, build_video_phase2_no_subtitle
import remix_api

FONTS_DIR = str(SKILL_DIR / "fonts")

# Server-side secret for HMAC auth tokens (stable across restarts)
_SERVER_SECRET = hashlib.sha256(f"vca-secret-{os.environ.get('ACCESS_PASSWORD', 'default')}".encode()).digest()

def _make_auth_token(password):
    """Create HMAC-based auth token from password + server secret."""
    return hmac.new(_SERVER_SECRET, password.encode(), hashlib.sha256).hexdigest()[:32]

# Global state — Module 1: Video Clip Assembler
# --- Session-based state isolation ---
_sessions = {}
_sessions_lock = threading.Lock()
_SESSION_TIMEOUT = 7200  # 2 hours


def _default_state():
    return {
        "clips": {},
        "task": None,
        "task_progress": 0,
        "task_status": "idle",
        "task_message": "",
        "task_stage": "",
        "output_path": None,
        "vocabulary": [],
        "language": "id",
        "build_data": None,
    }


def _default_remix_state():
    return {
        "library_path": "/data/素材库" if os.path.isdir("/data") else os.path.expanduser("~/Desktop/素材库"),
        "initialized": False,
        "video_type": "招商视频",
        "script_segments": [{"zh": "", "id": "", "zh_char_count": 0, "id_word_count": 0} for _ in range(5)],
        "frame_pairs": [None] * 4,
        "seedance_tasks": {},
        "seedance_videos": [None] * 5,
        "voiceover_segment_idx": None,
        "output_path": None,
        "task_status": "idle",
        "task_progress": 0,
        "task_message": "",
    }


def _get_session_id(handler):
    cookies = handler.headers.get("Cookie", "")
    for part in cookies.split(";"):
        part = part.strip()
        if part.startswith("sid="):
            return part[4:]
    return "default"


def _ensure_session(sid):
    with _sessions_lock:
        if sid not in _sessions:
            _sessions[sid] = {
                "state": _default_state(),
                "remix_state": _default_remix_state(),
                "last_access": time.time(),
            }
        _sessions[sid]["last_access"] = time.time()
        if len(_sessions) > 20:
            now = time.time()
            expired = [s for s, d in _sessions.items() if now - d["last_access"] > _SESSION_TIMEOUT]
            for s in expired:
                del _sessions[s]
        return _sessions[sid]


def get_state(handler):
    """Get per-session Module 1 state."""
    return _ensure_session(_get_session_id(handler))["state"]


def get_remix_state_by_handler(handler):
    """Get per-session Module 2 state."""
    return _ensure_session(_get_session_id(handler))["remix_state"]

# API Keys from env
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")

# Access control: single password in env var
ACCESS_PASSWORD = os.environ.get("ACCESS_PASSWORD", "")

LOGIN_PAGE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Video Clip Assembler</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#fafafa;display:flex;justify-content:center;align-items:center;height:100vh}
.login{background:#fff;border:1px solid #efefef;border-radius:16px;padding:40px;width:320px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.04)}
h1{font-size:20px;font-weight:700;color:#262626;margin-bottom:8px}p{color:#8e8e8e;font-size:13px;margin-bottom:24px}
input{width:100%;padding:12px 16px;border:1px solid #dbdbdb;border-radius:10px;font-size:14px;outline:none;text-align:center;letter-spacing:2px}
input:focus{border-color:#262626}
button{width:100%;padding:12px;background:#262626;color:#fff;border:none;border-radius:10px;font-size:14px;font-weight:600;cursor:pointer;margin-top:12px}
button:hover{background:#404040}.err{color:#ed4956;font-size:12px;margin-top:8px;display:none}</style></head>
<body><div class="login"><h1>Video Clip Assembler</h1><p>Please enter password</p>
<form onsubmit="return doLogin()"><input type="password" id="pw" placeholder="Password" autocomplete="off">
<button type="submit">Enter</button><div class="err" id="err">Wrong password</div></form></div>
<script>function doLogin(){var pw=document.getElementById('pw').value;
fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pw})})
.then(r=>r.json()).then(d=>{if(d.ok){location.reload()}else{document.getElementById('err').style.display='block'}});return false}</script>
</body></html>"""


class Handler(SimpleHTTPRequestHandler):
    """Custom HTTP handler with API routes."""

    def check_access(self):
        """Check if request has valid session cookie. Returns True if allowed."""
        if not ACCESS_PASSWORD:
            return True  # No password configured = open access
        cookie_header = self.headers.get("Cookie", "")
        for part in cookie_header.split(";"):
            part = part.strip()
            if part.startswith("session="):
                token = part.split("=", 1)[1]
                expected = _make_auth_token(ACCESS_PASSWORD)
                if hmac.compare_digest(token, expected):
                    return True
        return False

    def send_login_page(self):
        body = LOGIN_PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Filename")
        self.end_headers()

    def do_GET(self):
        if not self.check_access():
            parsed_check = urlparse(self.path)
            if parsed_check.path.startswith("/api/"):
                self.send_json({"error": "unauthorized"}, status=403)
            else:
                self.send_login_page()
            return

        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.serve_file(STATIC_DIR / "index.html", "text/html")
        elif path == "/app.js":
            self.serve_file(STATIC_DIR / "app.js", "application/javascript")
        elif path == "/style.css":
            self.serve_file(STATIC_DIR / "style.css", "text/css")
        elif path == "/api/status":
            self.api_status()
        elif path == "/api/download":
            self.api_download()
        elif path == "/api/clips":
            self.api_clips()
        elif path.startswith("/api/remix/"):
            remix_api.handle_get(self, path)
        elif path == "/remix.js":
            self.serve_file(STATIC_DIR / "remix.js", "application/javascript")
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Login endpoint doesn't require auth
        if path == "/api/login":
            self.api_login()
            return

        if not self.check_access():
            self.send_json({"error": "unauthorized"}, status=403)
            return

        if path.startswith("/api/remix/"):
            remix_api.handle_post(self, path)
        elif path == "/api/upload":
            self.api_upload()
        elif path == "/api/clear":
            self.api_clear_clips()
        elif path == "/api/transcribe":
            self.api_transcribe()
        elif path == "/api/keywords":
            self.api_keywords()
        elif path == "/api/keyword-categories":
            self.api_keyword_categories()
        elif path == "/api/build":
            self.api_build()
        elif path == "/api/continue-build":
            self.api_continue_build()
        elif path == "/api/vocabulary":
            self.api_vocabulary()
        else:
            self.send_error(404)

    def serve_file(self, filepath, content_type):
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_error(404)

    def read_json_body(self, max_size=1 * 1024 * 1024):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > max_size:
            raise ValueError(f"Request body too large: {content_length} bytes (max {max_size})")
        body = self.rfile.read(content_length)
        return json.loads(body) if body else {}

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    # --- API endpoints ---

    def api_login(self):
        """Handle password login."""
        data = self.read_json_body()
        password = data.get("password", "")
        if password == ACCESS_PASSWORD:
            token = _make_auth_token(ACCESS_PASSWORD)
            body = json.dumps({"ok": True}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Set-Cookie", f"session={token}; Path=/; Max-Age=31536000; SameSite=Lax; HttpOnly")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_json({"ok": False}, 401)

    def api_upload(self):
        """Handle single file upload (streaming, supports large files)."""
        state = get_state(self)
        raw_filename = self.headers.get("X-Filename", "")
        if not raw_filename:
            self.send_json({"error": "Missing X-Filename header"}, 400)
            return

        filename = os.path.basename(unquote(raw_filename))
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self.send_json({"error": "Empty file"}, 400)
            return
        max_upload = 200 * 1024 * 1024  # 200 MB (iPhone .mov files can be large)
        if content_length > max_upload:
            self.send_json({"error": f"文件太大 ({content_length // (1024*1024)} MB)，最大 200 MB"}, 413)
            return

        clip_id = str(uuid.uuid4())[:8]
        save_path = CLIPS_DIR / f"{clip_id}_{filename}"

        CHUNK = 64 * 1024
        remaining = content_length
        with open(save_path, "wb") as f:
            while remaining > 0:
                chunk = self.rfile.read(min(CHUNK, remaining))
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)

        # Check upload completeness
        if remaining > 0:
            if save_path.exists():
                save_path.unlink()
            self.send_json({"error": f"上传不完整（已接收 {content_length - remaining} / {content_length} 字节），请重试"}, 400)
            return

        # Validate file is readable
        import subprocess as _sp
        probe = _sp.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(save_path)],
            capture_output=True, text=True, timeout=30,
        )
        if probe.returncode != 0:
            if save_path.exists():
                save_path.unlink()
            self.send_json({"error": "文件已损坏（无法读取），请检查原文件是否完整后重新上传"}, 400)
            return

        state["clips"][clip_id] = {
            "path": str(save_path),
            "filename": filename,
            "sentences": [],
        }

        self.send_json({"id": clip_id, "filename": filename})

    def api_clear_clips(self):
        """Clear all clips before new batch upload."""
        state = get_state(self)
        state["clips"].clear()
        state["task_status"] = "idle"
        state["task_progress"] = 0
        state["task_message"] = ""
        state["task_stage"] = ""
        self.send_json({"status": "cleared"})

    def api_vocabulary(self):
        """Set custom vocabulary (proper nouns, brand names) and language for transcription."""
        state = get_state(self)
        data = self.read_json_body()
        vocab = data.get("vocabulary", [])
        state["vocabulary"] = [v.strip() for v in vocab if v.strip()]
        if "language" in data:
            state["language"] = data["language"]
        self.send_json({"status": "ok", "count": len(state["vocabulary"]), "language": state["language"]})

    def api_transcribe(self):
        """Start async transcription of all clips using Gemini."""
        state = get_state(self)
        if state["task_status"] in ("transcribing", "translating"):
            self.send_json({"error": "Task already running"}, 409)
            return

        if not GEMINI_API_KEY:
            self.send_json({"error": "GEMINI_API_KEY not set"}, 500)
            return

        vocabulary = state.get("vocabulary", [])
        language = state.get("language", "id")

        def run():
            try:
                clips = list(state["clips"].items())
                total = len(clips)
                state["task_status"] = "transcribing"
                state["task_progress"] = 0
                state["task_message"] = f"准备转录 {total} 个视频..."

                all_sentences = []

                for i, (clip_id, clip_info) in enumerate(clips):
                    state["task_progress"] = int(i / total * 50)
                    state["task_message"] = f"提取音频 ({i+1}/{total}): {clip_info['filename']}"
                    time.sleep(0.1)

                    state["task_message"] = f"Gemini 转录中 ({i+1}/{total}): {clip_info['filename']}"
                    sentences = transcribe_video(
                        clip_info["path"], GEMINI_API_KEY,
                        vocabulary=vocabulary if vocabulary else None,
                        language=language,
                    )

                    for s in sentences:
                        s["clip_id"] = clip_id
                        s["clip_filename"] = clip_info["filename"]
                        s["clip_path"] = clip_info["path"]

                    clip_info["sentences"] = sentences
                    all_sentences.extend(sentences)
                    state["task_progress"] = int((i + 1) / total * 50)
                    state["task_message"] = f"转录完成 ({i+1}/{total})，共 {len(sentences)} 句"

                # Translate
                state["task_status"] = "translating"
                state["task_progress"] = 55
                state["task_message"] = f"Gemini 翻译中... ({len(all_sentences)} 句)"

                if all_sentences:
                    translate_sentences(all_sentences, GEMINI_API_KEY, source_language=language)

                state["task_progress"] = 100
                state["task_status"] = "done"
                state["task_message"] = f"完成！共 {len(all_sentences)} 句"

            except Exception as e:
                state["task_status"] = "error"
                state["task_message"] = f"错误: {str(e)}"
                import traceback
                traceback.print_exc()

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        self.send_json({"status": "started"})

    def api_status(self):
        """Return current task status."""
        state = get_state(self)
        self.send_json({
            "status": state["task_status"],
            "progress": state["task_progress"],
            "message": state["task_message"],
            "stage": state.get("task_stage", ""),
        })

    def api_clips(self):
        """Return all clips with their sentences."""
        state = get_state(self)
        result = {}
        for clip_id, clip_info in state["clips"].items():
            result[clip_id] = {
                "filename": clip_info["filename"],
                "sentences": clip_info.get("sentences", []),
            }
        self.send_json(result)

    def api_keywords(self):
        """Match Chinese keywords to Indonesian words."""
        state = get_state(self)
        data = self.read_json_body()
        keywords = data.get("keywords", [])

        if not keywords:
            self.send_json({"error": "No keywords provided"}, 400)
            return

        if not GEMINI_API_KEY:
            self.send_json({"error": "GEMINI_API_KEY not set"}, 500)
            return

        all_sentences = []
        for clip_info in state["clips"].values():
            all_sentences.extend(clip_info.get("sentences", []))

        matches = match_keywords(keywords, all_sentences, GEMINI_API_KEY)
        self.send_json({"matches": matches})

    def api_keyword_categories(self):
        """Auto-detect keywords by category from transcription."""
        state = get_state(self)
        data = self.read_json_body()
        categories = data.get("categories", [])

        if not categories:
            self.send_json({"error": "No categories"}, 400)
            return

        if not GEMINI_API_KEY:
            self.send_json({"error": "GEMINI_API_KEY not set"}, 500)
            return

        # Gather all transcribed text
        all_sentences = []
        for clip_info in state["clips"].values():
            all_sentences.extend(clip_info.get("sentences", []))

        if not all_sentences:
            self.send_json({"matches": {}})
            return

        # Build context
        context_lines = []
        for s in all_sentences:
            context_lines.append(f"印尼语: {s['text']}")
            context_lines.append(f"中文: {s.get('translation', '')}")
            context_lines.append("")
        context = "\n".join(context_lines)

        cat_descriptions = {
            "numbers": "数字和数量词 (angka, jumlah) — e.g. dua, tiga, seratus, juta, ratusan",
            "time": "时间相关词 — e.g. hari, bulan, tahun, minggu, jam, sehari, setahun",
            "age": "年龄相关词 — e.g. tahun (when used for age), umur, usia",
            "brand": "品牌名、产品名、专有名词 — any proper nouns or brand mentions",
            "money": "金额和货币词 — e.g. rupiah, juta, miliar, ribu, harga",
            "emotion": "情感词和强调词 — e.g. beneran, banget, wow, serius, gila",
        }

        cat_list = ", ".join(f"{c} ({cat_descriptions.get(c, c)})" for c in categories)

        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)

        prompt = f"""Below is a transcription of Indonesian speech with Chinese translations.

{context}

Find ALL Indonesian words in the transcription that belong to these categories:
{cat_list}

Return a JSON object where keys are the Indonesian words found, and values are the category name.
ONLY include words that actually appear in the Indonesian transcription text above.

Format: {{"word1": "category", "word2": "category", ...}}
Return ONLY the JSON object, no explanation."""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        try:
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text.rsplit("```", 1)[0]
                text = text.strip()
            matches = json.loads(text)
        except (json.JSONDecodeError, IndexError):
            matches = {}

        self.send_json({"matches": matches})

    def api_build(self):
        """Phase 1: Trim + Concat, then pause for subtitle choice."""
        state = get_state(self)
        data = self.read_json_body()
        selections = data.get("selections", [])
        keyword_highlights = data.get("keywords", {})

        if not selections:
            self.send_json({"error": "No segments selected"}, 400)
            return

        if state["task_status"] == "building":
            self.send_json({"error": "Build already in progress"}, 409)
            return

        def progress_callback(stage, pct, msg):
            state["task_stage"] = stage
            state["task_progress"] = pct
            state["task_message"] = msg

        def run():
            try:
                state["task_status"] = "building"
                state["task_progress"] = 5
                state["task_message"] = "开始构建..."
                state["task_stage"] = "init"

                build_dir = TEMP_DIR / "build"
                build_dir.mkdir(exist_ok=True)

                result = build_video_phase1(
                    selections=selections,
                    temp_dir=str(build_dir),
                    progress_callback=progress_callback,
                )

                # Store phase1 result for phase2
                state["build_data"] = {
                    "concat_path": result["concat_path"],
                    "subtitle_segments": result["subtitle_segments"],
                    "keyword_highlights": keyword_highlights,
                    "build_dir": str(build_dir),
                }
                state["task_status"] = "subtitle_choice"
                state["task_stage"] = "subtitle_choice"
                state["task_progress"] = 50
                state["task_message"] = "拼接完成！请选择是否添加字幕"

            except Exception as e:
                state["task_status"] = "error"
                stderr_msg = getattr(e, 'stderr', b'')
                if isinstance(stderr_msg, bytes):
                    stderr_msg = stderr_msg.decode('utf-8', errors='replace')[-300:]
                state["task_message"] = f"构建错误: {str(e)}\n{stderr_msg}"
                import traceback
                traceback.print_exc()

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        self.send_json({"status": "building"})

    def api_continue_build(self):
        """Phase 2: Burn subtitles or finalize without."""
        state = get_state(self)
        data = self.read_json_body()
        burn_subtitle = data.get("burn_subtitle", True)

        if not state.get("build_data"):
            self.send_json({"error": "No build in progress"}, 400)
            return

        bd = state["build_data"]

        def progress_callback(stage, pct, msg):
            state["task_stage"] = stage
            state["task_progress"] = pct
            state["task_message"] = msg

        def run():
            try:
                state["task_status"] = "building"
                output_path = str(TEMP_DIR / "output.mp4")

                if burn_subtitle:
                    build_video_phase2_subtitle(
                        concat_path=bd["concat_path"],
                        subtitle_segments=bd["subtitle_segments"],
                        keyword_highlights=bd["keyword_highlights"],
                        temp_dir=bd["build_dir"],
                        output_path=output_path,
                        fonts_dir=FONTS_DIR,
                        progress_callback=progress_callback,
                    )
                else:
                    build_video_phase2_no_subtitle(
                        concat_path=bd["concat_path"],
                        output_path=output_path,
                        progress_callback=progress_callback,
                    )

                state["output_path"] = output_path
                state["task_status"] = "done"
                state["task_progress"] = 100
                state["build_data"] = None

                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                state["task_message"] = f"视频生成完成！({size_mb:.1f} MB)"

            except Exception as e:
                state["task_status"] = "error"
                stderr_msg = getattr(e, 'stderr', b'')
                if isinstance(stderr_msg, bytes):
                    stderr_msg = stderr_msg.decode('utf-8', errors='replace')[-300:]
                state["task_message"] = f"构建错误: {str(e)}\n{stderr_msg}"
                import traceback
                traceback.print_exc()

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        self.send_json({"status": "building"})

    def api_download(self):
        """Download the built video."""
        state = get_state(self)
        if not state["output_path"] or not os.path.exists(state["output_path"]):
            self.send_json({"error": "No output video available"}, 404)
            return

        filepath = state["output_path"]
        filesize = os.path.getsize(filepath)

        self.send_response(200)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Content-Length", str(filesize))
        self.send_header("Content-Disposition", 'attachment; filename="assembled.mp4"')
        self.end_headers()

        with open(filepath, "rb") as f:
            shutil.copyfileobj(f, self.wfile)

    def log_message(self, format, *args):
        """Quieter logging."""
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def main():
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8765))
    host = os.environ.get("HOST", "127.0.0.1")

    # Ensure dirs exist
    TEMP_DIR.mkdir(exist_ok=True)
    CLIPS_DIR.mkdir(exist_ok=True)

    class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
        daemon_threads = True

    server = ThreadedHTTPServer((host, port), Handler)
    print(f"Video Clip Assembler: http://localhost:{port}")
    print(f"  temp: {TEMP_DIR}")
    print(f"  Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
        server.shutdown()


if __name__ == "__main__":
    main()
