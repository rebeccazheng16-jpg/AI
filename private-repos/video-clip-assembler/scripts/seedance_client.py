"""
Seedance 1.5 Pro API client — extracted from seedance-video-gen skill.
Provides submit/poll/download for web backend integration.
"""

import urllib.request
import urllib.error
import json
import base64
import os
import time

API_KEY = os.environ.get("SEEDANCE_API_KEY", "")
MODEL = "doubao-seedance-1-5-pro-251215"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"

POLL_INTERVAL = 10
MAX_POLL_ATTEMPTS = 120


def _api_request(url, data=None, method="GET"):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")[:500]
        try:
            err_json = json.loads(err_body)
            msg = err_json.get("error", {}).get("message", err_body)
        except Exception:
            msg = err_body
        return None, f"HTTP {e.code}: {msg}"
    except urllib.error.URLError as e:
        return None, f"Network error: {e.reason}"


def _image_to_data_url(image_path):
    """Convert local image to base64 data URL. Rejects files >30MB (API limit)."""
    path = os.path.expanduser(image_path)
    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        data = f.read()

    if len(data) > 30 * 1024 * 1024:
        print(f"[SEEDANCE] Image too large (>{len(data)//1024//1024}MB > 30MB limit): {path}", flush=True)
        return None

    ext = os.path.splitext(path)[1].lower()
    mime_map = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".bmp": "image/bmp",
    }
    mime = mime_map.get(ext, "image/png")
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def submit_task(prompt, first_frame=None, last_frame=None,
                duration=8, ratio="9:16", resolution="720p",
                generate_audio=True):
    """Submit a Seedance video generation task. Returns task_id or None."""
    content = [{"type": "text", "text": prompt}]

    if first_frame:
        url = first_frame if first_frame.startswith("http") else _image_to_data_url(first_frame)
        if url:
            content.append({"type": "image_url", "image_url": {"url": url}, "role": "first_frame"})

    if last_frame:
        url = last_frame if last_frame.startswith("http") else _image_to_data_url(last_frame)
        if url:
            content.append({"type": "image_url", "image_url": {"url": url}, "role": "last_frame"})

    payload = {
        "model": MODEL,
        "content": content,
        "ratio": ratio,
        "resolution": resolution,
        "duration": duration,
        "generate_audio": generate_audio,
    }

    result, err = _api_request(BASE_URL, data=payload, method="POST")
    if err:
        return None, err
    task_id = result.get("id")
    if not task_id:
        return None, "No task ID in response"
    return task_id, None


def poll_task(task_id):
    """Poll task status. Returns {status, video_url, last_frame_url, error}."""
    url = f"{BASE_URL}/{task_id}"
    result, err = _api_request(url, method="GET")
    if err:
        return {"status": "error", "error": err}

    status = result.get("status", "unknown")
    content = result.get("content", {})

    return {
        "status": status,
        "video_url": content.get("video_url"),
        "last_frame_url": content.get("last_frame_url"),
        "error": result.get("error", {}).get("message", ""),
        "usage": result.get("usage", {}),
    }


def download_video(video_url, output_path):
    """Download video from URL to local path. Returns True on success."""
    try:
        req = urllib.request.Request(video_url)
        with urllib.request.urlopen(req, timeout=300) as resp:
            with open(output_path, "wb") as f:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def generate_video_sync(prompt, output_path, first_frame=None, last_frame=None,
                        duration=8, resolution="720p", progress_callback=None):
    """
    Full sync workflow: submit → poll → download.
    progress_callback(pct, message) for status updates.
    Returns output_path on success, None on failure.
    """
    if progress_callback:
        progress_callback(5, "Submitting Seedance task...")

    task_id, err = submit_task(prompt, first_frame, last_frame, duration, resolution=resolution)
    if err:
        print(f"[SEEDANCE] Submit failed: {err}", flush=True)
        if progress_callback:
            progress_callback(0, f"Submit failed: {err}")
        return None

    if progress_callback:
        progress_callback(10, f"Task submitted: {task_id}")

    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        time.sleep(POLL_INTERVAL)
        result = poll_task(task_id)
        status = result["status"]

        pct = min(10 + int(attempt / MAX_POLL_ATTEMPTS * 80), 90)
        if progress_callback:
            progress_callback(pct, f"Generating... ({attempt * POLL_INTERVAL}s)")

        if status == "succeeded":
            video_url = result.get("video_url")
            if not video_url:
                if progress_callback:
                    progress_callback(0, "No video URL in response")
                return None

            if progress_callback:
                progress_callback(92, "Downloading video...")

            if download_video(video_url, output_path):
                if progress_callback:
                    progress_callback(100, "Done")
                return output_path
            else:
                if progress_callback:
                    progress_callback(0, "Download failed")
                return None

        elif status in ("failed", "cancelled", "expired"):
            err_msg = result.get('error', '')
            print(f"[SEEDANCE] Task {task_id} {status}: {err_msg}", flush=True)
            if progress_callback:
                progress_callback(0, f"Task {status}: {err_msg}")
            return None

    if progress_callback:
        progress_callback(0, "Timeout after 20 minutes")
    return None
