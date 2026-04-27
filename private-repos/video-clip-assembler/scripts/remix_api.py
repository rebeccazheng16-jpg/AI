"""
AI Remix module API handlers.
All /api/remix/* endpoints are handled here.
"""

import json
import os
import threading
import time
import uuid
import base64
import urllib.request
import urllib.error
import tempfile
from pathlib import Path
from urllib.parse import unquote

# Paths — use /data (Railway persistent volume) in production, ~/Desktop locally
_DATA_ROOT = Path("/data") if os.path.isdir("/data") else Path(os.path.expanduser("~/Desktop"))
LIBRARY_PATH = _DATA_ROOT / "素材库"
REAL_CLIPS_DIR = LIBRARY_PATH / "实物素材"
AI_CLIPS_DIR = LIBRARY_PATH / "AI素材"
INIT_FLAG = REAL_CLIPS_DIR / ".initialized"
VIDEO_EXTS = ("*.mp4", "*.MP4", "*.mov", "*.MOV", "*.webm", "*.avi", "*.mkv", "*.MKV")


def _list_video_clips(directory):
    """List all video files in a directory across common formats."""
    clips = []
    for ext in VIDEO_EXTS:
        clips.extend(directory.glob(ext))
    return clips

# Indonesian word limit per 8s segment (~3-4 syllables/sec)
ID_WORD_LIMIT = 25
ZH_CHAR_LIMIT = 50


def get_remix_state(handler):
    """Get per-session remix state via handler's cookie."""
    from server import get_remix_state_by_handler
    return get_remix_state_by_handler(handler)


def _get_session_id(handler):
    """Get session ID from handler cookie for path isolation."""
    from server import _get_session_id as srv_get_sid
    return srv_get_sid(handler)


def _session_tmp_dir(handler, subdir):
    """Get a session-isolated temp directory under /tmp/remix_<subdir>_<sid>/."""
    sid = _get_session_id(handler)
    safe_sid = sid[:16].replace("/", "_").replace("..", "_")
    path = os.path.join(tempfile.gettempdir(), f"remix_{subdir}_{safe_sid}")
    os.makedirs(path, exist_ok=True)
    return path


# ── Asset Library ──

def handle_init_library(handler):
    """Create asset library directories (auto-setup, no local path needed)."""
    try:
        REAL_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
        AI_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
        INIT_FLAG.touch()  # Auto-initialize, no separate verify step needed

        state = get_remix_state(handler)
        state["initialized"] = True

        clip_count = len(list(_list_video_clips(REAL_CLIPS_DIR)))

        handler.send_json({
            "status": "ok",
            "library_path": str(LIBRARY_PATH),
            "clip_count": clip_count,
            "initialized": True,
        })
    except Exception as e:
        handler.send_json({"error": str(e)}, 500)


def handle_library_status(handler):
    """Return asset library status."""
    exists = REAL_CLIPS_DIR.exists()
    clip_count = len(list(_list_video_clips(REAL_CLIPS_DIR))) if exists else 0
    initialized = INIT_FLAG.exists()

    # Auto-update remix_state
    state = get_remix_state(handler)
    state["initialized"] = initialized

    handler.send_json({
        "exists": exists,
        "initialized": initialized,
        "clip_count": clip_count,
        "min_clips": 2,
        "library_path": str(LIBRARY_PATH),
    })


def handle_upload_clip(handler):
    """Upload a real footage clip to the asset library (streaming)."""
    raw_filename = handler.headers.get("X-Filename", "")
    if not raw_filename:
        handler.send_json({"error": "Missing X-Filename header"}, 400)
        return

    filename = os.path.basename(unquote(raw_filename))
    content_length = int(handler.headers.get("Content-Length", 0))
    if content_length == 0:
        handler.send_json({"error": "Empty file"}, 400)
        return
    max_upload = 200 * 1024 * 1024  # 200 MB (iPhone .mov files can be large)
    if content_length > max_upload:
        handler.send_json({"error": f"文件太大 ({content_length // (1024*1024)} MB)，最大 200 MB"}, 413)
        return

    # Ensure directory exists
    REAL_CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate unique filename to avoid collisions
    clip_id = str(uuid.uuid4())[:8]
    save_path = REAL_CLIPS_DIR / f"{clip_id}_{filename}"

    CHUNK = 64 * 1024
    remaining = content_length
    with open(save_path, "wb") as f:
        while remaining > 0:
            chunk = handler.rfile.read(min(CHUNK, remaining))
            if not chunk:
                break
            f.write(chunk)
            remaining -= len(chunk)

    # Check upload completeness — truncated file = moov atom missing = unusable
    if remaining > 0:
        if save_path.exists():
            save_path.unlink()
        handler.send_json({"error": f"上传不完整（已接收 {content_length - remaining} / {content_length} 字节），请重试"}, 400)
        return

    # Validate the uploaded file is actually readable by ffmpeg
    import subprocess
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(save_path)],
        capture_output=True, text=True, timeout=30,
    )
    if probe.returncode != 0:
        stderr = probe.stderr.strip()[-200:] if probe.stderr else ""
        if save_path.exists():
            save_path.unlink()
        handler.send_json({"error": f"文件已损坏（无法读取），请检查原文件是否完整后重新上传。{stderr}"}, 400)
        return

    # Auto-trim to 8s if longer: take the middle 8 seconds
    try:
        duration = float(probe.stdout.strip())
        if duration > 8.5:
            start = (duration - 8) / 2
            trimmed_path = save_path.parent / f"{save_path.stem}_8s{save_path.suffix}"
            subprocess.run(
                ["ffmpeg", "-i", str(save_path), "-ss", f"{start:.2f}", "-t", "8",
                 "-c:v", "copy", "-c:a", "copy", "-y", str(trimmed_path)],
                capture_output=True, check=True, timeout=30,
            )
            save_path.unlink()
            shutil.move(str(trimmed_path), str(save_path))
            print(f"[CLIP] Trimmed {filename}: {duration:.1f}s → 8s (start={start:.1f}s)", flush=True)
    except Exception as e:
        print(f"[CLIP] Trim check skipped: {e}", flush=True)

    clip_count = len(list(_list_video_clips(REAL_CLIPS_DIR)))

    handler.send_json({
        "filename": filename,
        "path": str(save_path),
        "clip_count": clip_count,
    })


def handle_finalize_library(handler):
    """Mark asset library as initialized (skip count check)."""
    REAL_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    INIT_FLAG.touch()
    state = get_remix_state(handler)
    state["initialized"] = True
    clip_count = len(list(_list_video_clips(REAL_CLIPS_DIR)))
    handler.send_json({"status": "ok", "clip_count": clip_count})


def handle_list_clips(handler):
    """List all real footage clips in the library."""
    if not REAL_CLIPS_DIR.exists():
        handler.send_json({"clips": []})
        return

    clips = []
    for f in sorted(_list_video_clips(REAL_CLIPS_DIR)):
        size_mb = f.stat().st_size / (1024 * 1024)
        clips.append({
            "filename": f.name,
            "size_mb": round(size_mb, 1),
        })

    print(f"[LIST-CLIPS] REAL_CLIPS_DIR={REAL_CLIPS_DIR}, exists={REAL_CLIPS_DIR.exists()}, clips={len(clips)}", flush=True)
    handler.send_json({"clips": clips})


def handle_delete_clip(handler):
    """Delete a single real footage clip by filename."""
    import json
    body = handler.rfile.read(int(handler.headers.get("Content-Length", 0)))
    data = json.loads(body) if body else {}
    filename = data.get("filename", "")
    if not filename:
        handler.send_json({"error": "Missing filename"}, 400)
        return

    target = REAL_CLIPS_DIR / filename
    if not target.exists():
        handler.send_json({"error": f"文件不存在: {filename}"}, 404)
        return

    # Safety: ensure path is within REAL_CLIPS_DIR
    if REAL_CLIPS_DIR not in target.resolve().parents and target.resolve().parent != REAL_CLIPS_DIR:
        handler.send_json({"error": "Invalid path"}, 400)
        return

    target.unlink()
    clip_count = len(list(_list_video_clips(REAL_CLIPS_DIR)))
    handler.send_json({"status": "ok", "deleted": filename, "clip_count": clip_count})


# ── Script Editing ──

def handle_get_defaults(handler):
    """Return default script segments (without exposing prompts)."""
    from prompt_templates import get_segment_info
    info = get_segment_info()
    handler.send_json({"segments": info})


def handle_save_script(handler):
    """Save 5 script segments (Chinese + Indonesian text)."""
    data = handler.read_json_body()
    segments = data.get("segments", [])

    if len(segments) not in (5, 6):
        handler.send_json({"error": "需要 5 个段落"}, 400)
        return

    state = get_remix_state(handler)
    result = []
    for i, seg in enumerate(segments):
        zh_text = seg.get("zh", "").strip()
        char_count = len(zh_text)
        result.append({
            "zh": zh_text,
            "id": state["script_segments"][i].get("id", "") if i < len(state["script_segments"]) else "",
            "zh_char_count": char_count,
            "over_limit": char_count > ZH_CHAR_LIMIT,
        })

    state["script_segments"] = result
    handler.send_json({"segments": result, "zh_char_limit": ZH_CHAR_LIMIT})


def handle_translate_script(handler):
    """Translate Chinese script to colloquial Indonesian via Gemini (async)."""
    state = get_remix_state(handler)

    # Reset status so polling doesn't see stale 'done' from previous task
    state["task_status"] = "idle"
    state["task_progress"] = 0
    state["task_message"] = ""

    # Accept segments from request body (frontend may not have saved yet)
    data = handler.read_json_body()
    if data.get("segments"):
        for i, seg in enumerate(data["segments"]):
            if i < len(state["script_segments"]):
                state["script_segments"][i]["zh"] = seg.get("zh", "")
                if seg.get("id"):
                    state["script_segments"][i]["id"] = seg["id"]

    segments = state.get("script_segments", [])

    zh_texts = [s.get("zh", "") for s in segments]
    if not any(zh_texts):
        handler.send_json({"error": "没有中文文案可翻译"}, 400)
        return

    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        handler.send_json({"error": "GEMINI_API_KEY not set"}, 500)
        return

    def run():
        try:
            state["task_status"] = "translating"
            state["task_progress"] = 10
            state["task_message"] = "Gemini 翻译中..."

            import google.generativeai as genai
            genai.configure(api_key=api_key)

            numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(zh_texts) if t)

            prompt = f"""Terjemahkan teks Mandarin berikut ke bahasa Indonesia LISAN yang natural untuk video TikTok.

ATURAN PENTING:
- Gunakan bahasa sehari-hari Jakarta, BUKAN bahasa formal/baku
- Pakai "aku/kamu" bukan "saya/Anda"
- Pakai singkatan alami: "nggak" bukan "tidak", "udah" bukan "sudah", "banget" bukan "sangat"
- Jaga nama brand asli (Tulandut, dll)
- Setiap segmen MAKSIMAL {ID_WORD_LIMIT} kata
- HAPUS jejak AI: jangan pakai "menawarkan", "memberikan", "memastikan", "menunjukkan", "mencerminkan"
- Tulis seperti orang sungguhan ngobrol, bukan seperti iklan
- ANGKA: Tulis semua angka dengan HURUF Indonesia, BUKAN angka Arab. Contoh: "8" → "delapan", "600" → "enam ratus", "5 orang" → "lima orang". Ini penting supaya TTS tidak tiba-tiba bicara bahasa Inggris

Kembalikan JSON array: ["terjemahan1", "terjemahan2", ...] (5 item, string kosong jika input kosong)

Teks:
{numbered}"""

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)

            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text.rsplit("```", 1)[0]
                text = text.strip()

            translations = json.loads(text)

            for i, trans in enumerate(translations):
                if i < len(state["script_segments"]):
                    id_text = str(trans).strip()
                    word_count = len(id_text.split()) if id_text else 0
                    state["script_segments"][i]["id"] = id_text
                    state["script_segments"][i]["id_word_count"] = word_count
                    state["script_segments"][i]["id_over_limit"] = word_count > ID_WORD_LIMIT

            state["task_status"] = "done"
            state["task_progress"] = 100
            state["task_message"] = "翻译完成"

        except Exception as e:
            state["task_status"] = "error"
            state["task_message"] = f"翻译错误: {str(e)}"
            import traceback
            traceback.print_exc()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    handler.send_json({"status": "started"})


def handle_translate_one(handler):
    """Translate a single segment (synchronous, fast)."""
    data = handler.read_json_body()
    idx = data.get("idx")
    zh_text = data.get("zh", "").strip()

    if idx is None or not zh_text:
        handler.send_json({"error": "Missing idx or zh text"}, 400)
        return

    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        handler.send_json({"error": "GEMINI_API_KEY not set"}, 500)
        return

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        prompt = f"""Terjemahkan kalimat Mandarin ini ke bahasa Indonesia LISAN untuk TikTok.
Pakai bahasa sehari-hari Jakarta: "aku/kamu", "nggak/udah/banget".
Jaga nama brand asli. Maksimal {ID_WORD_LIMIT} kata.
HAPUS jejak AI. Tulis seperti ngobrol biasa.
ANGKA: Tulis semua angka dengan HURUF Indonesia (contoh: "8" → "delapan", "600" → "enam ratus").

Mandarin: {zh_text}

Kembalikan HANYA terjemahan Indonesia, tanpa penjelasan."""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        id_text = response.text.strip().strip('"').strip("'")

        # Update state
        state = get_remix_state(handler)
        if idx < len(state["script_segments"]):
            state["script_segments"][idx]["zh"] = zh_text
            state["script_segments"][idx]["id"] = id_text
            state["script_segments"][idx]["id_word_count"] = len(id_text.split())

        handler.send_json({"idx": idx, "id": id_text, "word_count": len(id_text.split())})

    except Exception as e:
        handler.send_json({"error": str(e)}, 500)


def handle_check_compliance(handler):
    """Check script against TikTok + WhatsApp banned words (server-side)."""
    # Read current editor segments from request body (not saved state)
    data = handler.read_json_body()
    segments = data.get("segments") if data else None
    if not segments:
        # Fallback to saved state if request body is empty
        state = get_remix_state(handler)
        segments = state.get("script_segments", [])

    # Load banned words from TikTok content policy
    banned_words = _get_banned_words()

    violations = []
    for i, seg in enumerate(segments):
        seg_violations = []
        for field in ["zh", "id"]:
            text = seg.get(field, "")
            if not text:
                continue
            lower = text.lower()
            for bw in banned_words:
                if bw["word"].lower() in lower:
                    seg_violations.append({
                        "word": bw["word"],
                        "category": bw["cat"],
                        "field": field,
                        "segment": i,
                    })
        if seg_violations:
            violations.append({"segment": i, "issues": seg_violations})

    handler.send_json({
        "clean": len(violations) == 0,
        "violation_count": sum(len(v["issues"]) for v in violations),
        "violations": violations,
    })


def _get_banned_words():
    """Combined banned words list for TikTok + WhatsApp compliance."""
    return [
        # TikTok absolute claims
        {"word": "pertama", "cat": "absolute"},
        {"word": "satu-satunya", "cat": "absolute"},
        {"word": "terbaik", "cat": "absolute"},
        {"word": "termurah", "cat": "absolute"},
        {"word": "nomor satu", "cat": "absolute"},
        {"word": "best seller", "cat": "absolute"},
        {"word": "第一", "cat": "absolute"},
        {"word": "唯一", "cat": "absolute"},
        {"word": "最好", "cat": "absolute"},
        {"word": "最强", "cat": "absolute"},
        {"word": "最低价", "cat": "absolute"},
        # TikTok medical claims
        {"word": "menyembuhkan", "cat": "medical"},
        {"word": "mengobati", "cat": "medical"},
        {"word": "obat", "cat": "medical"},
        {"word": "permanen", "cat": "medical"},
        {"word": "治愈", "cat": "medical"},
        {"word": "治疗", "cat": "medical"},
        {"word": "永久", "cat": "medical"},
        # TikTok beauty red lines
        {"word": "menghilangkan jerawat", "cat": "beauty"},
        {"word": "menghilangkan kerutan", "cat": "beauty"},
        {"word": "memutihkan", "cat": "beauty"},
        {"word": "祛痘", "cat": "beauty"},
        {"word": "消除皱纹", "cat": "beauty"},
        {"word": "美白", "cat": "beauty"},
        # TikTok exaggerated
        {"word": "100% efektif", "cat": "exaggerated"},
        {"word": "dijamin", "cat": "exaggerated"},
        {"word": "instan", "cat": "exaggerated"},
        {"word": "100%有效", "cat": "exaggerated"},
        {"word": "立即见效", "cat": "exaggerated"},
        # WhatsApp specific - spam/fraud
        {"word": "chain letter", "cat": "wa_spam"},
        {"word": "pyramid scheme", "cat": "wa_spam"},
        {"word": "传销", "cat": "wa_spam"},
        {"word": "连锁信", "cat": "wa_spam"},
        # Muslim sensitivity - avoid in Indonesian Muslim content
        {"word": "babi", "cat": "muslim"},
        {"word": "alkohol", "cat": "muslim"},
        {"word": "bir", "cat": "muslim"},
        {"word": "wine", "cat": "muslim"},
        {"word": "haram", "cat": "muslim"},
        {"word": "猪", "cat": "muslim"},
        {"word": "酒精", "cat": "muslim"},
        # Numbers as digits (should be spelled out to avoid TTS English)
        {"word": "100%", "cat": "number_tts"},
        {"word": "1000", "cat": "number_tts"},
    ]


# ── Status Polling ──

def handle_remix_status(handler):
    """Return current remix task status + segments data when done."""
    state = get_remix_state(handler)
    resp = {
        "status": state.get("task_status", "idle"),
        "progress": state.get("task_progress", 0),
        "message": state.get("task_message", ""),
    }
    # Include segments data so frontend can read translations
    if state.get("task_status") == "done":
        resp["segments"] = state.get("script_segments", [])
    handler.send_json(resp)


# ── Gemini Image Gen + Seedance Video Gen ──

def _generate_image_gemini(prompt, api_key, output_path, aspect_ratio="9:16", reference_image=None):
    """Call Gemini image generation API. Returns saved image path.
    reference_image: path to a local image file to use as face/style reference.
    """
    model = "gemini-3-pro-image-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    parts = []

    # Add reference image first (if provided)
    if reference_image and os.path.exists(reference_image):
        with open(reference_image, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(reference_image)[1].lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
        mime = mime_map.get(ext, "image/jpeg")
        parts.append({"inline_data": {"mime_type": mime, "data": img_data}})
        prompt = f"Use Image 1 as the COMPLETE VISUAL REFERENCE — generate the EXACT SAME PERSON with identical facial features, face shape, skin tone, hijab color and wrapping style, clothing color and style, jewelry, background setting, furniture, plants, and lighting direction. ONLY change hand position and facial expression as described below. Everything else — outfit, hijab, room, camera angle — must remain IDENTICAL to Image 1.\n\n{prompt}"

    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 1.0,
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
            }
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    candidates = result.get("candidates", [])
    if not candidates:
        feedback = result.get("promptFeedback", {})
        raise Exception(f"No candidates. Feedback: {feedback}")

    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        inline_data = part.get("inline_data") or part.get("inlineData")
        if inline_data:
            img_b64 = inline_data.get("data", "")
            mime = inline_data.get("mime_type") or inline_data.get("mimeType", "image/png")

            ext = ".jpg" if ("jpeg" in mime or "jpg" in mime) else ".png"
            # Fix extension if needed
            base, _ = os.path.splitext(output_path)
            final_path = base + ext

            with open(final_path, "wb") as f:
                f.write(base64.b64decode(img_b64))
            return final_path

    raise Exception("No image data in Gemini response")


def handle_generate_frames(handler):
    """Generate 4 chain frame images (F0-F3) using Gemini for S1/S2/S3."""
    state = get_remix_state(handler)
    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        handler.send_json({"error": "GEMINI_API_KEY not set"}, 500)
        return

    # Reset status BEFORE starting thread so polling doesn't see stale "done"
    state["task_status"] = "generating_frames"
    state["task_progress"] = 0
    state["task_message"] = "Starting..."

    frame_dir = _session_tmp_dir(handler, "frames")

    def run():
        try:
            state["task_status"] = "generating_frames"
            state["task_progress"] = 0
            state["task_message"] = "Randomizing character..."
            print("[FRAMES] Starting frame generation...", flush=True)

            from prompt_templates import randomize_variables, build_chain_frame_prompt

            variables = randomize_variables()
            state["current_variables"] = variables

            # 4 chain frames: F0→F1→F2→F3, producing 3 videos: S1(F0→F1), S2(F1→F2), S3(F2→F3)
            total = 4
            frames = []
            anchor_path = None  # F0 becomes face anchor for all subsequent frames

            for i in range(total):
                pct = int((i / total) * 90) + 5
                state["task_progress"] = pct
                label = "anchor" if i == 0 else "ref→F0"
                state["task_message"] = f"Gemini: F{i} ({label}) ({i+1}/{total})..."

                prompt = build_chain_frame_prompt(i, variables)

                output_path = os.path.join(frame_dir, f"F{i}.png")

                # First frame = no reference; subsequent frames = use F0 as face anchor
                ref = anchor_path if i > 0 else None

                try:
                    print(f"[FRAMES] Calling Gemini for F{i} (ref={'yes' if ref else 'no'})...", flush=True)
                    saved_path = _generate_image_gemini(prompt, api_key, output_path, reference_image=ref)
                    print(f"[FRAMES] F{i} done: {saved_path}", flush=True)
                    frames.append({
                        "chain_idx": i,
                        "path": saved_path,
                        "status": "done",
                    })
                    # Save first successful frame as anchor
                    if i == 0:
                        anchor_path = saved_path
                except Exception as e:
                    err_str = str(e)
                    # Auto-retry once on Gemini HTTP 500 (server-side flake)
                    if "500" in err_str:
                        print(f"[FRAMES] F{i} got HTTP 500, auto-retrying in 3s...", flush=True)
                        time.sleep(3)
                        try:
                            saved_path = _generate_image_gemini(prompt, api_key, output_path, reference_image=ref)
                            print(f"[FRAMES] F{i} retry OK: {saved_path}", flush=True)
                            frames.append({
                                "chain_idx": i,
                                "path": saved_path,
                                "status": "done",
                            })
                            if i == 0:
                                anchor_path = saved_path
                            continue
                        except Exception as e2:
                            err_str = str(e2)
                            print(f"[FRAMES] F{i} retry also FAILED: {err_str}", flush=True)

                    print(f"[FRAMES] F{i} FAILED: {err_str}", flush=True)
                    frames.append({
                        "chain_idx": i,
                        "path": None,
                        "status": "error",
                        "error": err_str,
                    })

            state["frame_pairs"] = frames

            failed = [f for f in frames if f["status"] == "error"]
            if failed:
                state["task_status"] = "done"
                state["task_progress"] = 100
                state["task_message"] = f"Generated {total - len(failed)}/{total} frames ({len(failed)} failed)"
            else:
                state["task_status"] = "done"
                state["task_progress"] = 100
                state["task_message"] = f"All {total} frames generated"

        except Exception as e:
            state["task_status"] = "error"
            state["task_message"] = f"Frame generation failed: {str(e)}"
            import traceback
            traceback.print_exc()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    handler.send_json({"status": "started"})


MAX_REGEN = 3


def handle_regenerate_frame(handler):
    """Regenerate a single chain frame with user feedback, max 3 times per frame."""
    state = get_remix_state(handler)
    data = handler.read_json_body()
    chain_idx = data.get("chain_idx")
    feedback = data.get("feedback", "").strip()

    if chain_idx is None or chain_idx not in (0, 1, 2, 3):
        handler.send_json({"error": "Invalid chain_idx (must be 0-3)"}, 400)
        return

    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        handler.send_json({"error": "GEMINI_API_KEY not set"}, 500)
        return

    # Check retry count
    retries = state.get("frame_retries", {})
    key = f"chain_{chain_idx}"
    count = retries.get(key, 0)
    if count >= MAX_REGEN:
        handler.send_json({"error": "max_retries", "message": "Retry limit reached (3/3)", "retries": count}, 400)
        return

    try:
        from prompt_templates import build_chain_frame_prompt
        variables = state.get("current_variables")
        if not variables:
            from prompt_templates import randomize_variables
            variables = randomize_variables()

        base_prompt = build_chain_frame_prompt(chain_idx, variables)

        # Append user feedback to prompt
        if feedback:
            base_prompt += f"\n\nIMPORTANT modification: {feedback}"

        frame_dir = _session_tmp_dir(handler, "frames")
        output_path = os.path.join(frame_dir, f"F{chain_idx}.png")

        # Use F0 as face anchor (unless regenerating F0 itself)
        anchor = None
        if chain_idx != 0:
            for f in state.get("frame_pairs", []):
                if f is None:
                    continue
                if f.get("chain_idx") == 0 and f.get("status") == "done":
                    anchor = f.get("path")
                    break

        saved_path = _generate_image_gemini(base_prompt, api_key, output_path, reference_image=anchor)

        # Update state
        retries[key] = count + 1
        state["frame_retries"] = retries

        # Update frame_pairs
        for f in state.get("frame_pairs", []):
            if f is None:
                continue
            if f.get("chain_idx") == chain_idx:
                f["path"] = saved_path
                f["status"] = "done"
                break

        handler.send_json({
            "status": "done",
            "retries": count + 1,
            "max": MAX_REGEN,
            "chain_idx": chain_idx,
        })

    except Exception as e:
        handler.send_json({"error": str(e)}, 500)


def handle_frame_image(handler, query_string):
    """Serve a generated frame image. GET /api/remix/frame-image?idx=0"""
    from urllib.parse import parse_qs
    params = parse_qs(query_string)
    chain_idx = int(params.get("idx", ["-1"])[0])

    state = get_remix_state(handler)
    for f in state.get("frame_pairs", []):
        if f is None:
            continue
        if f.get("chain_idx") == chain_idx and f.get("status") == "done":
            path = f.get("path")
            if path and os.path.exists(path):
                import shutil
                ext = os.path.splitext(path)[1].lower()
                mime = "image/png" if ext == ".png" else "image/jpeg"
                filesize = os.path.getsize(path)
                handler.send_response(200)
                handler.send_header("Content-Type", mime)
                handler.send_header("Content-Length", str(filesize))
                handler.send_header("Cache-Control", "no-cache")
                handler.end_headers()
                with open(path, "rb") as img:
                    shutil.copyfileobj(img, handler.wfile)
                return

    handler.send_error(404)


def handle_frame_status(handler):
    """Return all frame statuses including retry counts."""
    state = get_remix_state(handler)
    frames = state.get("frame_pairs", [])
    retries = state.get("frame_retries", {})

    result = []
    for f in frames:
        if f is None:
            continue
        key = f"chain_{f.get('chain_idx')}"
        result.append({
            "chain_idx": f.get("chain_idx"),
            "status": f.get("status", "pending"),
            "error": f.get("error", ""),
            "retries": retries.get(key, 0),
            "max_retries": MAX_REGEN,
        })

    handler.send_json({"frames": result})


def handle_start_seedance(handler):
    """Start parallel Seedance video generation for all 5 segments."""
    state = get_remix_state(handler)

    # Sync segments from request body (frontend may have translations not yet saved)
    data = handler.read_json_body()
    if data.get("segments"):
        for i, seg in enumerate(data["segments"]):
            if i < len(state["script_segments"]):
                if seg.get("zh"):
                    state["script_segments"][i]["zh"] = seg["zh"]
                if seg.get("id"):
                    state["script_segments"][i]["id"] = seg["id"]

    segments = state.get("script_segments", [])

    # Resolution from request (default 720p)
    video_resolution = data.get("resolution", "720p")
    if video_resolution not in ("720p", "1080p"):
        video_resolution = "720p"
    state["video_resolution"] = video_resolution

    seedance_key = os.environ.get("SEEDANCE_API_KEY", "")
    if not seedance_key:
        handler.send_json({"error": "SEEDANCE_API_KEY not set"}, 500)
        return

    from prompt_templates import build_seedance_prompt, SEGMENT_TYPES
    variables = state.get("current_variables")
    if not variables:
        from prompt_templates import randomize_variables
        variables = randomize_variables()
        state["current_variables"] = variables

    # Get generated chain frames for S1/S2/S3
    frame_pairs = state.get("frame_pairs", [])

    def _get_chain_frame(chain_idx):
        for f in frame_pairs:
            if f is None:
                continue
            if f.get("chain_idx") == chain_idx and f.get("status") == "done":
                path = f.get("path")
                if path and os.path.exists(path):
                    return path
        return None

    # Initialize task tracking
    state["seedance_tasks"] = {}
    state["seedance_videos"] = [None] * 5

    build_dir = _session_tmp_dir(handler, "seedance")

    def run_single(idx):
        task_key = f"seg_{idx}"
        state["seedance_tasks"][task_key] = {"status": "starting", "progress": 0, "error": ""}
        print(f"[SEEDANCE] run_single({idx}) starting, segments_count={len(segments)}", flush=True)

        try:
            id_text = segments[idx].get("id", "") if idx < len(segments) else ""
            print(f"[SEEDANCE] seg_{idx} id_text='{id_text[:30]}...' " if id_text else f"[SEEDANCE] seg_{idx} id_text=EMPTY", flush=True)
            if not id_text:
                state["seedance_tasks"][task_key] = {"status": "skipped", "progress": 100, "error": "No script"}
                return

            prompt = build_seedance_prompt(idx, id_text, variables)
            output_path = os.path.join(build_dir, f"seg_{idx}.mp4")

            # Frame mapping: S1=F0→F1, S2=F1→F2, S3=F1 only, S4=F1 only, S5=F2→F3
            FRAME_MAP = {
                0: (0, 1),       # S1: F0→F1
                1: (1, 2),       # S2: F1→F2
                2: (1, None),    # S3: F1 only (audio gen, video from real footage)
                3: (1, None),    # S4: F1 only (audio gen, video from real footage)
                4: (2, 3),       # S5 CTA: F2→F3
            }
            f_first, f_last = FRAME_MAP.get(idx, (None, None))
            first_frame = _get_chain_frame(f_first) if f_first is not None else None
            last_frame = _get_chain_frame(f_last) if f_last is not None else None
            print(f"[SEEDANCE] seg_{idx}: first_frame(F{f_first})={first_frame}, last_frame(F{f_last})={last_frame}", flush=True)

            # All segments MUST have at least first_frame
            if not first_frame:
                state["seedance_tasks"][task_key] = {
                    "status": "error", "progress": 0,
                    "error": f"Missing frame F{f_first} — go back to Step 3 and generate frames first",
                }
                return
            # S1/S2/S5 also need last_frame
            if f_last is not None and not last_frame:
                state["seedance_tasks"][task_key] = {
                    "status": "error", "progress": 0,
                    "error": f"Missing frame F{f_last} — go back to Step 3 and generate frames first",
                }
                return

            from seedance_client import generate_video_sync

            def progress_cb(pct, msg):
                state["seedance_tasks"][task_key] = {"status": "generating", "progress": pct, "error": "", "message": msg}

            result = generate_video_sync(prompt, output_path, first_frame=first_frame, last_frame=last_frame, duration=8, resolution=video_resolution, progress_callback=progress_cb)

            if result:
                state["seedance_videos"][idx] = output_path
                state["seedance_tasks"][task_key] = {"status": "done", "progress": 100, "error": ""}
            else:
                # Get error from last progress callback message
                last_msg = state["seedance_tasks"].get(task_key, {}).get("message", "")
                err_detail = last_msg if last_msg and "failed" in last_msg.lower() else "Generation failed"
                print(f"[SEEDANCE] seg_{idx} failed: {err_detail}", flush=True)
                state["seedance_tasks"][task_key] = {"status": "error", "progress": 0, "error": err_detail}

        except Exception as e:
            print(f"[SEEDANCE] seg_{idx} EXCEPTION: {e}", flush=True)
            import traceback
            traceback.print_exc()
            state["seedance_tasks"][task_key] = {"status": "error", "progress": 0, "error": str(e)}

    # Launch in batches of 2 to avoid Seedance API concurrency limits
    def run_batched():
        batch_size = 2
        for batch_start in range(0, 5, batch_size):
            batch_end = min(batch_start + batch_size, 5)
            threads = []
            for idx in range(batch_start, batch_end):
                t = threading.Thread(target=run_single, args=(idx,), daemon=True)
                t.start()
                threads.append(t)
            for t in threads:
                t.join()

    t = threading.Thread(target=run_batched, daemon=True)
    t.start()

    handler.send_json({"status": "started", "total": 5})


def handle_seedance_status(handler):
    """Return per-segment Seedance generation status (includes current script text)."""
    state = get_remix_state(handler)
    tasks = state.get("seedance_tasks", {})
    videos = state.get("seedance_videos", [None] * 5)
    script_segments = state.get("script_segments", [])

    segments = []
    all_done = True
    for idx in range(5):
        task_key = f"seg_{idx}"
        task = tasks.get(task_key, {"status": "pending", "progress": 0, "error": ""})
        script_id = script_segments[idx].get("id", "") if idx < len(script_segments) else ""
        segments.append({
            "idx": idx,
            "status": task.get("status", "pending"),
            "progress": task.get("progress", 0),
            "error": task.get("error", ""),
            "message": task.get("message", ""),
            "has_video": videos[idx] is not None,
            "script": script_id,
        })
        if task.get("status") not in ("done", "skipped", "error"):
            all_done = False

    handler.send_json({
        "segments": segments,
        "all_done": all_done,
    })


def handle_retry_seedance(handler):
    """Retry a single Seedance segment without re-running the rest.
    Accepts optional new_script to update the segment's Indonesian text before retrying."""
    state = get_remix_state(handler)
    data = handler.read_json_body()
    idx = data.get("idx")
    if idx is None or idx < 0 or idx > 4:
        handler.send_json({"error": "Invalid segment index"}, 400)
        return

    # If new script text provided, update the segment before retrying
    new_script = data.get("new_script", "").strip()
    if new_script:
        segments = state.get("script_segments", [])
        if idx < len(segments):
            segments[idx]["id"] = new_script
            segments[idx]["id_word_count"] = len(new_script.split())

    # Ensure task tracking exists (in case retry is called before full generation)
    if "seedance_tasks" not in state:
        state["seedance_tasks"] = {}
    if "seedance_videos" not in state:
        state["seedance_videos"] = [None] * 5
    while len(state["seedance_videos"]) < 5:
        state["seedance_videos"].append(None)

    segments = state.get("script_segments", [])
    seedance_key = os.environ.get("SEEDANCE_API_KEY", "")
    if not seedance_key:
        handler.send_json({"error": "SEEDANCE_API_KEY not set"}, 500)
        return

    from prompt_templates import build_seedance_prompt
    variables = state.get("current_variables")
    if not variables:
        from prompt_templates import randomize_variables
        variables = randomize_variables()
        state["current_variables"] = variables

    frame_pairs = state.get("frame_pairs", [])
    video_resolution = state.get("video_resolution", "720p")

    def _get_chain_frame(chain_idx):
        for f in frame_pairs:
            if f is None:
                continue
            if f.get("chain_idx") == chain_idx and f.get("status") == "done":
                path = f.get("path")
                if path and os.path.exists(path):
                    return path
        return None

    build_dir = _session_tmp_dir(handler, "seedance")

    def run():
        task_key = f"seg_{idx}"
        state["seedance_tasks"][task_key] = {"status": "starting", "progress": 0, "error": ""}
        try:
            id_text = segments[idx].get("id", "") if idx < len(segments) else ""
            if not id_text:
                state["seedance_tasks"][task_key] = {"status": "skipped", "progress": 100, "error": "No script"}
                return

            prompt = build_seedance_prompt(idx, id_text, variables)
            output_path = os.path.join(build_dir, f"seg_{idx}.mp4")

            FRAME_MAP = {
                0: (0, 1), 1: (1, 2), 2: (1, None), 3: (1, None), 4: (2, 3),
            }
            f_first, f_last = FRAME_MAP.get(idx, (None, None))
            first_frame = _get_chain_frame(f_first) if f_first is not None else None
            last_frame = _get_chain_frame(f_last) if f_last is not None else None

            if not first_frame:
                state["seedance_tasks"][task_key] = {"status": "error", "progress": 0, "error": f"Missing frame F{f_first}"}
                return
            if f_last is not None and not last_frame:
                state["seedance_tasks"][task_key] = {"status": "error", "progress": 0, "error": f"Missing frame F{f_last}"}
                return

            from seedance_client import generate_video_sync

            def progress_cb(pct, msg):
                state["seedance_tasks"][task_key] = {"status": "generating", "progress": pct, "error": "", "message": msg}

            result = generate_video_sync(prompt, output_path, first_frame=first_frame, last_frame=last_frame, duration=8, resolution=video_resolution, progress_callback=progress_cb)

            if result:
                state["seedance_videos"][idx] = output_path
                state["seedance_tasks"][task_key] = {"status": "done", "progress": 100, "error": ""}
            else:
                last_msg = state["seedance_tasks"].get(task_key, {}).get("message", "")
                err_detail = last_msg if last_msg and "failed" in last_msg.lower() else "Generation failed"
                state["seedance_tasks"][task_key] = {"status": "error", "progress": 0, "error": err_detail}

        except Exception as e:
            print(f"[SEEDANCE] retry seg_{idx} EXCEPTION: {e}", flush=True)
            state["seedance_tasks"][task_key] = {"status": "error", "progress": 0, "error": str(e)}

    t = threading.Thread(target=run, daemon=True)
    t.start()
    handler.send_json({"status": "retrying", "idx": idx})


def handle_assemble(handler):
    """Final video assembly: AI videos + real footage with voiceover."""
    state = get_remix_state(handler)
    videos = state.get("seedance_videos", [None] * 5)
    # Ensure videos list is always length 5
    while len(videos) < 5:
        videos.append(None)

    # Check we have videos
    ready_count = sum(1 for v in videos if v is not None)
    if ready_count < 3:  # Need at least S1, S2, and S5
        handler.send_json({"error": f"Need at least 3 videos, have {ready_count}"}, 400)
        return

    # Pre-check: real footage clips still exist (files lost on server restart)
    real_clips = sorted(_list_video_clips(REAL_CLIPS_DIR))
    if len(real_clips) < 1:
        handler.send_json({"error": "素材丢失：服务器重启后上传的素材被清空，请返回 Step 0 重新上传实物素材"}, 400)
        return

    # Reset status BEFORE starting thread so polling doesn't see stale "done"
    state["task_status"] = "assembling"
    state["task_progress"] = 0
    state["task_message"] = "Starting assembly..."

    # Precompute session-scoped build dir before thread (handler not available in thread)
    build_dir = _session_tmp_dir(handler, "assembly")

    def run():
        try:
            import subprocess
            import random
            import shutil
            from video_processor import get_ffmpeg_path

            ffmpeg = get_ffmpeg_path()
            state["task_status"] = "assembling"
            state["task_progress"] = 5
            state["task_message"] = "Starting assembly..."

            # Step 1: Get real footage clips for S3/S4
            state["task_progress"] = 10
            state["task_message"] = "Preparing real footage for S3/S4..."

            real_clips = sorted(_list_video_clips(REAL_CLIPS_DIR))
            if len(real_clips) < 1:
                raise Exception("Need at least 1 real footage clip — upload in Step 0")
            # If only 1 clip, reuse it for both S3 and S4
            if len(real_clips) < 2:
                real_clips.append(real_clips[0])

            # S3/S4: combine Seedance audio (from single-frame video) with real footage video
            real_combined = []
            ffprobe = shutil.which("ffprobe") or ffmpeg.replace("ffmpeg", "ffprobe")

            # Pre-check: verify real footage clips are readable
            for rc in real_clips:
                probe_check = subprocess.run(
                    [ffprobe, "-v", "error", "-show_entries", "format=duration",
                     "-of", "csv=p=0", str(rc)],
                    capture_output=True, text=True, timeout=30,
                )
                if probe_check.returncode != 0:
                    fname = os.path.basename(str(rc))
                    raise Exception(f"实拍素材 {fname} 已损坏（无法读取），请在 Step 0 重新上传")

            for i, seg_idx in enumerate([2, 3]):
                seedance_vid = videos[seg_idx]
                real_clip = real_clips[i] if i < len(real_clips) else real_clips[-1]
                if seedance_vid:
                    # Verify Seedance video has audio track
                    probe = subprocess.run(
                        [ffprobe, "-v", "error", "-select_streams", "a",
                         "-show_entries", "stream=codec_type", "-of", "csv=p=0",
                         seedance_vid],
                        capture_output=True, text=True, timeout=30,
                    )
                    has_audio = "audio" in (probe.stdout or "")
                    if not has_audio:
                        seg_name = f"S{seg_idx + 1}"
                        raise Exception(f"{seg_name} 视频没有音轨（人声），请重新生成 {seg_name}")

                    # Step 1: Extract audio from Seedance to standalone file
                    audio_path = os.path.join(build_dir, f"audio_{i}.aac")
                    subprocess.run(
                        [ffmpeg, "-i", seedance_vid, "-vn", "-acodec", "aac", "-y", audio_path],
                        capture_output=True, check=True, timeout=300,
                    )
                    # Step 2: Merge real footage video + extracted audio (explicit mapping!)
                    combined = os.path.join(build_dir, f"real_combined_{i}.mp4")
                    try:
                        # Try stream copy first (fast, low memory)
                        subprocess.run(
                            [
                                ffmpeg, "-i", str(real_clip), "-i", audio_path,
                                "-map", "0:v", "-map", "1:a",
                                "-c:v", "copy", "-c:a", "copy", "-shortest", "-t", "8",
                                "-y", combined,
                            ],
                            capture_output=True, check=True, timeout=300,
                        )
                    except subprocess.CalledProcessError:
                        # Fallback: re-encode (handles iPhone HEVC .mov etc.)
                        subprocess.run(
                            [
                                ffmpeg, "-i", str(real_clip), "-i", audio_path,
                                "-map", "0:v", "-map", "1:a",
                                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                                "-c:a", "aac", "-b:a", "128k",
                                "-shortest", "-t", "8",
                                "-y", combined,
                            ],
                            capture_output=True, check=True, timeout=300,
                        )
                    real_combined.append(combined)
                else:
                    # Fallback: use real clip as-is (silent)
                    real_combined.append(str(real_clip))

            # Step 2: Build final segment list
            state["task_progress"] = 40
            state["task_message"] = "Normalizing video formats..."

            all_inputs = [
                videos[0],           # S1 AI video
                videos[1],           # S2 AI video
                real_combined[0],    # S3: real footage + Seedance audio
                real_combined[1],    # S4: real footage + Seedance audio
                videos[4],           # S5 CTA AI video
            ]

            # Use actual resolution from Seedance generation (Hobby plan: 8GB RAM)
            res = state.get("video_resolution", "720p")
            if res == "1080p":
                scale_w, scale_h = 1080, 1920
            else:
                scale_w, scale_h = 720, 1280

            final_segments = []
            for i, input_path in enumerate(all_inputs):
                if input_path is None:
                    continue
                normalized = os.path.join(build_dir, f"norm_{i}.mp4")
                # Use ultrafast preset + higher CRF for 1080p to avoid OOM on Railway (512MB)
                preset = "ultrafast" if res == "1080p" else "fast"
                crf = "23" if res == "1080p" else "18"
                subprocess.run(
                    [
                        ffmpeg, "-i", input_path,
                        "-vf", f"scale={scale_w}:{scale_h}:force_original_aspect_ratio=decrease,pad={scale_w}:{scale_h}:(ow-iw)/2:(oh-ih)/2",
                        "-r", "30", "-c:v", "libx264", "-preset", preset, "-crf", crf,
                        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
                        "-t", "8", "-pix_fmt", "yuv420p",
                        "-y", normalized,
                    ],
                    capture_output=True, check=True, timeout=300,
                )
                final_segments.append(normalized)

            # Step 5: Concatenate
            state["task_progress"] = 80
            state["task_message"] = "Concatenating final video..."

            concat_list = os.path.join(build_dir, "concat.txt")
            with open(concat_list, "w") as f:
                for seg in final_segments:
                    f.write(f"file '{seg}'\n")

            output_path = os.path.join(build_dir, "final_40s.mp4")
            subprocess.run(
                [
                    ffmpeg, "-f", "concat", "-safe", "0", "-i", concat_list,
                    "-c", "copy", "-y", output_path,
                ],
                capture_output=True, check=True, timeout=300,
            )

            # Also save to asset library
            AI_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_copy = str(AI_CLIPS_DIR / f"remix_{timestamp}.mp4")
            shutil.copy2(output_path, final_copy)

            state["output_path"] = output_path
            state["task_status"] = "done"
            state["task_progress"] = 100

            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            state["task_message"] = f"Done! {size_mb:.1f} MB"

        except subprocess.CalledProcessError as e:
            state["task_status"] = "error"
            stderr = ""
            if e.stderr:
                stderr = e.stderr.decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else str(e.stderr)
                stderr = stderr[-300:]
            state["task_message"] = f"Assembly failed: {stderr or str(e)}"
            import traceback
            traceback.print_exc()
        except Exception as e:
            state["task_status"] = "error"
            state["task_message"] = f"Assembly failed: {str(e)}"
            import traceback
            traceback.print_exc()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    handler.send_json({"status": "started"})


def handle_keyword_categories(handler):
    """Auto-detect keywords by category from confirmed script segments."""
    data = handler.read_json_body()
    categories = data.get("categories", [])
    if not categories:
        handler.send_json({"error": "No categories"}, 400)
        return

    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        handler.send_json({"error": "GEMINI_API_KEY not set"}, 500)
        return

    state = get_remix_state(handler)
    segments = state.get("script_segments", [])
    if not segments:
        handler.send_json({"matches": {}})
        return

    context_lines = []
    for s in segments:
        context_lines.append(f"印尼语: {s.get('id', '')}")
        context_lines.append(f"中文: {s.get('zh', '')}")
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
    genai.configure(api_key=api_key)

    prompt = f"""Below is a script with Indonesian text and Chinese translations.

{context}

Find ALL Indonesian words in the text that belong to these categories:
{cat_list}

Return a JSON object where keys are the Indonesian words found, and values are the category name.
ONLY include words that actually appear in the Indonesian text above.

Format: {{"word1": "category", "word2": "category", ...}}
Return ONLY the JSON object, no explanation."""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()
        matches = json.loads(text)
    except (json.JSONDecodeError, IndexError, ValueError):
        matches = {}
    except Exception as e:
        handler.send_json({"error": str(e)}, 500)
        return

    handler.send_json({"matches": matches})


def handle_keywords(handler):
    """Match Chinese keywords to Indonesian words in the confirmed script."""
    data = handler.read_json_body()
    keywords = data.get("keywords", [])
    if not keywords:
        handler.send_json({"error": "No keywords provided"}, 400)
        return

    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        handler.send_json({"error": "GEMINI_API_KEY not set"}, 500)
        return

    state = get_remix_state(handler)
    segments = state.get("script_segments", [])

    # Build sentences list compatible with match_keywords
    sentences = [{"text": s.get("id", ""), "translation": s.get("zh", "")} for s in segments]

    from translator import match_keywords
    matches = match_keywords(keywords, sentences, api_key)
    handler.send_json({"matches": matches})


def handle_burn_subtitles(handler):
    """Transcribe assembled video audio and burn subtitles."""
    state = get_remix_state(handler)
    output_path = state.get("output_path")
    if not output_path or not os.path.exists(output_path):
        handler.send_json({"error": "No assembled video to add subtitles to"}, 400)
        return

    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        handler.send_json({"error": "GEMINI_API_KEY not set"}, 500)
        return

    # Read keywords from POST body
    data = handler.read_json_body()
    keyword_highlights = data.get("keywords", {})

    state["task_status"] = "idle"

    # Precompute session-scoped build dir before thread (handler not available in thread)
    build_dir = _session_tmp_dir(handler, "subtitle")

    def run():
        try:
            import subprocess
            from video_processor import get_ffmpeg_path
            from ass_generator import generate_ass

            ffmpeg = get_ffmpeg_path()
            state["task_status"] = "subtitling"
            state["task_progress"] = 10
            state["task_message"] = "Transcribing audio..."

            # Use sentence-level transcription (same as Module 1's proven approach).
            # This gives natural sentence boundaries with timestamps from Gemini,
            # then generate_ass() handles splitting long sentences via
            # smart_split_words() which respects punctuation and conjunctions.
            from transcriber import transcribe_video
            sentences = transcribe_video(output_path, api_key, language="id")
            print(f"[SUBTITLE] Got {len(sentences)} sentence-level segments", flush=True)

            state["task_progress"] = 50
            state["task_message"] = f"Transcribed {len(sentences)} sentences, generating subtitles..."

            # sentences already have natural timestamps from Gemini:
            # [{"text": "Guys, udah 5 orang tanya...", "start": 0.5, "end": 3.2}, ...]
            # generate_ass() will auto-split long sentences via split_segment() +
            # smart_split_words() which breaks at commas and Indonesian conjunctions.
            subtitle_segments = sentences

            SKILL_DIR = Path(__file__).parent.parent
            fonts_dir = str(SKILL_DIR / "fonts")
            ass_path = os.path.join(build_dir, "subtitles.ass")
            generate_ass(subtitle_segments, keyword_highlights, ass_path)

            state["task_progress"] = 75
            state["task_message"] = "Burning subtitles..."

            # Step 4: Burn subtitles
            subtitled_path = os.path.join(build_dir, "final_subtitled.mp4")
            safe_ass = ass_path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
            safe_fonts = fonts_dir.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
            subprocess.run(
                [
                    ffmpeg, "-i", output_path,
                    "-vf", f"ass={safe_ass}:fontsdir={safe_fonts}",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                    "-c:a", "aac", "-b:a", "128k",
                    "-pix_fmt", "yuv420p",
                    "-y", subtitled_path,
                ],
                capture_output=True, check=True, timeout=300,
            )

            state["output_path"] = subtitled_path
            state["task_status"] = "done"
            state["task_progress"] = 100

            size_mb = os.path.getsize(subtitled_path) / (1024 * 1024)
            state["task_message"] = f"Subtitles added! {size_mb:.1f} MB"

        except Exception as e:
            state["task_status"] = "error"
            state["task_message"] = f"Subtitle failed: {str(e)}"
            import traceback
            traceback.print_exc()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    handler.send_json({"status": "started"})


def handle_download(handler):
    """Download assembled video."""
    state = get_remix_state(handler)
    output_path = state.get("output_path")

    # Fallback: scan session-scoped /tmp for the most recent remix output if session lost
    if not output_path or not os.path.exists(output_path):
        import glob
        sub_dir = _session_tmp_dir(handler, "subtitle")
        asm_dir = _session_tmp_dir(handler, "assembly")
        candidates = glob.glob(os.path.join(sub_dir, "final_subtitled.mp4")) + \
                     glob.glob(os.path.join(asm_dir, "final_40s.mp4"))
        candidates = [c for c in candidates if os.path.exists(c)]
        if candidates:
            output_path = max(candidates, key=os.path.getmtime)
            state["output_path"] = output_path

    if not output_path or not os.path.exists(output_path):
        handler.send_json({"error": "Video not found. The server was restarted — please go back and regenerate."}, 404)
        return

    import shutil
    filesize = os.path.getsize(output_path)
    handler.send_response(200)
    handler.send_header("Content-Type", "video/mp4")
    handler.send_header("Content-Length", str(filesize))
    handler.send_header("Content-Disposition", 'attachment; filename="remix_40s.mp4"')
    handler.end_headers()
    with open(output_path, "rb") as f:
        shutil.copyfileobj(f, handler.wfile)


def handle_download_segment(handler, query_string):
    """Download/stream a single Seedance segment video (S1-S5).
    Supports HTTP Range requests for <video> element playback."""
    from urllib.parse import parse_qs
    params = parse_qs(query_string)
    idx = int(params.get("idx", ["-1"])[0])
    state = get_remix_state(handler)
    videos = state.get("seedance_videos", [None] * 5)

    if idx < 0 or idx >= len(videos) or videos[idx] is None or not os.path.exists(videos[idx]):
        handler.send_json({"error": "Segment not available"}, 404)
        return

    path = videos[idx]
    filesize = os.path.getsize(path)
    labels = ["S1_past", "S2_turning", "S3_entry", "S4_fission", "S5_cta"]
    fname = f"{labels[idx] if idx < len(labels) else f'seg_{idx}'}.mp4"

    # Handle Range requests for <video> streaming
    range_header = handler.headers.get("Range")
    if range_header:
        # Parse "bytes=start-end"
        import re
        m = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if m:
            start = int(m.group(1))
            if start >= filesize:
                handler.send_response(416)
                handler.send_header("Content-Range", f"bytes */{filesize}")
                handler.end_headers()
                return
            end = int(m.group(2)) if m.group(2) else filesize - 1
            end = min(end, filesize - 1)
            length = end - start + 1
            handler.send_response(206)
            handler.send_header("Content-Type", "video/mp4")
            handler.send_header("Content-Range", f"bytes {start}-{end}/{filesize}")
            handler.send_header("Content-Length", str(length))
            handler.send_header("Accept-Ranges", "bytes")
            handler.end_headers()
            try:
                with open(path, "rb") as f:
                    f.seek(start)
                    remaining = length
                    while remaining > 0:
                        chunk = f.read(min(65536, remaining))
                        if not chunk:
                            break
                        handler.wfile.write(chunk)
                        remaining -= len(chunk)
            except (ConnectionResetError, BrokenPipeError):
                pass  # Client disconnected mid-transfer
            return

    # Full file response (inline for preview, or download)
    handler.send_response(200)
    handler.send_header("Content-Type", "video/mp4")
    handler.send_header("Content-Length", str(filesize))
    handler.send_header("Accept-Ranges", "bytes")
    handler.send_header("Content-Disposition", f'inline; filename="{fname}"')
    handler.end_headers()
    try:
        with open(path, "rb") as f:
            import shutil
            shutil.copyfileobj(f, handler.wfile)
    except (ConnectionResetError, BrokenPipeError):
        pass  # Client disconnected mid-transfer


def handle_reset(handler):
    """Reset remix state for a fresh start."""
    state = get_remix_state(handler)
    state["video_type"] = "招商视频"
    # Keep script_segments — user doesn't want to re-enter text
    state["frame_pairs"] = [None] * 4
    state["seedance_tasks"] = {}
    state["seedance_videos"] = [None] * 5
    state["voiceover_segment_idx"] = None
    state["output_path"] = None
    state["task_status"] = "idle"
    state["task_progress"] = 0
    state["task_message"] = ""
    state["current_variables"] = None
    state["frame_retries"] = {}
    state["video_resolution"] = "720p"

    # Clean up session temp files
    try:
        import shutil
        sid = _get_session_id(handler)
        safe_sid = sid[:16].replace("/", "_").replace("..", "_")
        tmp_base = tempfile.gettempdir()
        for prefix in ("remix_frames_", "remix_seedance_", "remix_subtitle_", "remix_assembly_"):
            d = os.path.join(tmp_base, f"{prefix}{safe_sid}")
            if os.path.isdir(d):
                shutil.rmtree(d, ignore_errors=True)
    except Exception:
        pass

    handler.send_json({"status": "reset"})


# ── Route Dispatcher ──

def handle_get(handler, path):
    """Dispatch GET /api/remix/* requests."""
    route = path.replace("/api/remix/", "").rstrip("/")

    routes = {
        "library-status": handle_library_status,
        "clips": handle_list_clips,
        "list-clips": handle_list_clips,
        "status": handle_remix_status,
        "seedance-status": handle_seedance_status,
        "defaults": handle_get_defaults,
        "frame-status": handle_frame_status,
    }

    fn = routes.get(route)
    if fn:
        fn(handler)
    elif route == "download":
        handle_download(handler)
    elif route.startswith("download-segment"):
        qs = getattr(handler, 'path', '').split("?", 1)[1] if "?" in getattr(handler, 'path', '') else ""
        handle_download_segment(handler, qs)
    elif route.startswith("frame-image"):
        # Get query string from original handler.path (server strips it from path)
        full = getattr(handler, 'path', '')
        qs = full.split("?", 1)[1] if "?" in full else ""
        handle_frame_image(handler, qs)
    else:
        handler.send_error(404)


def handle_post(handler, path):
    """Dispatch POST /api/remix/* requests."""
    route = path.replace("/api/remix/", "").rstrip("/")

    routes = {
        "init-library": handle_init_library,
        "finalize-library": handle_finalize_library,
        "upload-clip": handle_upload_clip,
        "delete-clip": handle_delete_clip,
        "save-script": handle_save_script,
        "translate": handle_translate_script,
        "translate-one": handle_translate_one,
        "check-compliance": handle_check_compliance,
        "generate-frames": handle_generate_frames,
        "regenerate-frame": handle_regenerate_frame,
        "start-seedance": handle_start_seedance,
        "retry-seedance": handle_retry_seedance,
        "assemble": handle_assemble,
        "burn-subtitles": handle_burn_subtitles,
        "keyword-categories": handle_keyword_categories,
        "keywords": handle_keywords,
        "reset": handle_reset,
    }

    fn = routes.get(route)
    if fn:
        fn(handler)
    else:
        handler.send_error(404)
