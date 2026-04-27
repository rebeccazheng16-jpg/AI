"""
Gemini-based transcription for Indonesian audio/video.
Uploads file via Gemini File API, then asks for timestamped transcription.
Supports custom vocabulary (brand names, proper nouns).
"""

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import google.generativeai as genai


def get_ffmpeg_path():
    """Get ffmpeg path — prefer system ffmpeg, fallback to imageio_ffmpeg."""
    import shutil
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def extract_audio(video_path: str, output_path: str) -> str:
    """Extract audio from video as WAV (no external codec needed)."""
    ffmpeg = get_ffmpeg_path()
    # Use WAV pcm_s16le — universally supported, no libmp3lame needed
    wav_path = output_path.rsplit(".", 1)[0] + ".wav"
    cmd = [
        ffmpeg, "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        wav_path
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=300)
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"ffmpeg audio extraction failed (code {result.returncode}):\n{stderr[-1000:]}")
    return wav_path


LANGUAGE_MAP = {
    "id": ("Indonesian (Bahasa Indonesia)", "keep informal words (nggak, beneran, etc.)"),
    "ko": ("Korean (한국어)", "keep colloquial expressions and particles"),
    "ja": ("Japanese (日本語)", "keep casual forms (だよ, じゃん, etc.)"),
    "zh": ("Chinese (中文)", "keep colloquial expressions"),
    "auto": ("auto-detect the language", "keep colloquial expressions"),
}


def transcribe_with_gemini(audio_path: str, api_key: str, vocabulary: list = None, language: str = "id") -> list:
    """
    Transcribe audio using Gemini.
    Upload file → ask for timestamped transcription → parse JSON.

    vocabulary: optional list of proper nouns/brand names to help recognition.
    language: language code (id/ko/ja/zh/auto).

    Returns list of sentence dicts:
    [{"text": "wow beneran ya", "start": 2.05, "end": 5.10}, ...]
    """
    genai.configure(api_key=api_key)

    # Upload audio file
    mime = "audio/wav" if audio_path.endswith(".wav") else "audio/mpeg"
    uploaded = genai.upload_file(audio_path, mime_type=mime)

    # Wait for processing
    while uploaded.state.name == "PROCESSING":
        time.sleep(1)
        uploaded = genai.get_file(uploaded.name)

    if uploaded.state.name == "FAILED":
        raise RuntimeError(f"Gemini file upload failed: {uploaded.state}")

    # Build vocabulary hint
    vocab_hint = ""
    if vocabulary:
        vocab_list = ", ".join(vocabulary)
        vocab_hint = f"""
IMPORTANT - These proper nouns / brand names may appear in the audio. Listen carefully for them:
{vocab_list}
When you hear any of these words (or something that sounds similar), transcribe them EXACTLY as listed above.
"""

    lang_name, lang_tip = LANGUAGE_MAP.get(language, LANGUAGE_MAP["auto"])
    if language == "auto":
        lang_line = "Auto-detect the language of this audio and transcribe it with precise timestamps."
    else:
        lang_line = f"Transcribe this {lang_name} audio with precise timestamps."

    prompt = f"""{lang_line}
{vocab_hint}
Return ONLY a JSON array, each element is one sentence/phrase:
[
  {{"text": "transcribed text here", "start": 0.0, "end": 2.5}},
  {{"text": "next sentence", "start": 2.8, "end": 5.1}},
  ...
]

Rules:
- Split at EVERY sentence-ending punctuation (period, question mark, exclamation mark)
- Prefer shorter segments: ideally 1-5 seconds, one sentence per segment
- If a sentence is very short (< 1 second), it's OK to keep it as its own segment
- Do NOT merge multiple sentences into one segment
- Timestamps in seconds with 1 decimal precision
- Transcribe exactly what is said, {lang_tip}
- Return ONLY the JSON array, no markdown, no explanation"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content([uploaded, prompt])

    # Parse response
    text = response.text.strip()
    # Strip markdown code fence if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

    try:
        sentences = json.loads(text)
    except json.JSONDecodeError:
        start_idx = text.find("[")
        end_idx = text.rfind("]")
        if start_idx != -1 and end_idx != -1:
            sentences = json.loads(text[start_idx:end_idx + 1])
        else:
            raise ValueError(f"Could not parse Gemini response as JSON: {text[:200]}")

    # Clean up uploaded file
    try:
        genai.delete_file(uploaded.name)
    except Exception:
        pass

    # Normalize
    result = []
    for s in sentences:
        if isinstance(s, dict) and s.get("text", "").strip():
            result.append({
                "text": s["text"].strip(),
                "start": float(s.get("start", 0)),
                "end": float(s.get("end", 0)),
                "words": [],
            })

    return result


def transcribe_words(video_path: str, api_key: str, language: str = "id") -> list:
    """
    Word-level transcription: returns list of {"word": str, "start": float, "end": float}.
    Used for precise subtitle alignment in remix module.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_path = tmp.name

    try:
        audio_path = extract_audio(video_path, audio_path)
        genai.configure(api_key=api_key)

        mime = "audio/wav"
        uploaded = genai.upload_file(audio_path, mime_type=mime)
        while uploaded.state.name == "PROCESSING":
            time.sleep(1)
            uploaded = genai.get_file(uploaded.name)
        if uploaded.state.name == "FAILED":
            raise RuntimeError(f"Gemini file upload failed: {uploaded.state}")

        lang_name, lang_tip = LANGUAGE_MAP.get(language, LANGUAGE_MAP["auto"])

        prompt = f"""Transcribe this {lang_name} audio with WORD-LEVEL timestamps.

Return ONLY a JSON array where each element is ONE WORD with its precise timing:
[
  {{"word": "Dulu", "start": 0.0, "end": 0.3}},
  {{"word": "aku", "start": 0.35, "end": 0.5}},
  ...
]

Rules:
- ONE word per element, not phrases or sentences
- Timestamps in seconds with 1-2 decimal precision
- Include ALL words spoken, nothing skipped
- Transcribe exactly what is said, {lang_tip}
- Return ONLY the JSON array, no markdown, no explanation"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([uploaded, prompt])

        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()

        words = json.loads(text)

        try:
            genai.delete_file(uploaded.name)
        except Exception:
            pass

        result = []
        for w in words:
            if isinstance(w, dict) and w.get("word", "").strip():
                result.append({
                    "word": w["word"].strip(),
                    "start": float(w.get("start", 0)),
                    "end": float(w.get("end", 0)),
                })
        return result
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)


def transcribe_video(video_path: str, api_key: str, vocabulary: list = None, language: str = "id") -> list:
    """
    Full pipeline: video → audio → Gemini → sentences.
    Returns list of sentence dicts with timestamps.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_path = tmp.name

    try:
        audio_path = extract_audio(video_path, audio_path)
        sentences = transcribe_with_gemini(audio_path, api_key, vocabulary=vocabulary, language=language)
        return sentences
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)
