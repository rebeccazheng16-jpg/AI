"""
ASS subtitle generator with keyword highlighting and smart segmentation.
Keywords get 2x font size + yellow color.
Long sentences are split into multiple subtitle events.
"""

# Indonesian conjunctions/prepositions for smart splitting
SPLIT_WORDS = {
    "dan", "tapi", "tetapi", "karena", "yang", "kalau", "jadi",
    "supaya", "agar", "atau", "untuk", "dengan", "dari", "ke",
    "di", "pada", "ini", "itu", "lalu", "terus", "kemudian",
    "makanya", "soalnya", "juga", "sih", "kan", "nih", "tuh",
    "kayak", "seperti", "waktu", "ketika", "setelah", "sebelum",
}

MAX_WORDS_PER_LINE = 6


def smart_split_words(words, max_words=MAX_WORDS_PER_LINE):
    """
    Split a list of words into chunks of max_words,
    preferring natural break points (after conjunctions, commas).
    """
    if len(words) <= max_words:
        return [words]

    chunks = []
    current = []

    for i, word in enumerate(words):
        current.append(word)

        # Check if we should split here
        at_limit = len(current) >= max_words
        near_limit = len(current) >= max_words - 1
        remaining = len(words) - i - 1

        # Don't create tiny last chunk (< 2 words)
        if remaining > 0 and remaining < 2 and at_limit:
            continue

        # Split after comma
        if word.endswith(",") and near_limit and remaining > 1:
            chunks.append(current)
            current = []
            continue

        # Split after conjunction (if next word starts new clause)
        clean = word.strip(".,!?;:").lower()
        if clean in SPLIT_WORDS and near_limit and remaining > 1:
            chunks.append(current)
            current = []
            continue

        # Hard split at max
        if at_limit and remaining > 0:
            chunks.append(current)
            current = []

    if current:
        chunks.append(current)

    return chunks


def split_segment(segment, max_words=MAX_WORDS_PER_LINE):
    """
    Split a long segment into multiple shorter subtitle events.
    Time is distributed proportionally by word count.
    """
    words = segment.get("text", "").split()
    if len(words) <= max_words:
        return [segment]

    chunks = smart_split_words(words, max_words)
    total_duration = segment["end"] - segment["start"]
    total_words = len(words)

    result = []
    current_time = segment["start"]

    for chunk_words in chunks:
        chunk_duration = total_duration * (len(chunk_words) / total_words)
        result.append({
            "text": " ".join(chunk_words),
            "start": current_time,
            "end": current_time + chunk_duration,
            "words": [],
        })
        current_time += chunk_duration

    return result


def generate_ass(
    segments: list,
    keyword_map: dict,
    output_path: str,
    base_font_size: int = 90,
    keyword_font_size: int = 180,
    video_width: int = 1080,
    video_height: int = 1920,
):
    """
    Generate ASS subtitle file with keyword highlighting.
    Long sentences are auto-split into multiple subtitle events.

    segments: list of {
        "text": "wow beneran ya",
        "start": 2.05,
        "end": 5.10,
        "words": [...]
    }

    keyword_map: {"beneran": true, "juta": true, ...}
    """
    # Normalize keyword set (lowercase)
    keywords = {k.lower().strip() for k in keyword_map if keyword_map[k]}

    # Split long segments first
    split_segments = []
    for seg in segments:
        split_segments.extend(split_segment(seg))

    header = f"""[Script Info]
Title: Video Clip Assembler Subtitles
ScriptType: v4.00+
PlayResX: {video_width}
PlayResY: {video_height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans CJK SC,{base_font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,40,40,580,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []

    for seg in split_segments:
        start_ts = format_ass_time(seg["start"])
        end_ts = format_ass_time(seg["end"])

        text = seg.get("text", "")
        highlighted = highlight_words(text, keywords, keyword_font_size)

        line = f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{highlighted}"
        events.append(line)

    content = header + "\n".join(events) + "\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


def highlight_words(text: str, keywords: set, keyword_font_size: int) -> str:
    """
    Apply ASS override tags to highlight keywords.
    Keywords get yellow color + larger font.
    """
    words = text.split()
    parts = []

    for word in words:
        clean = word.strip(".,!?;:\"'()[]{}").lower()

        if clean in keywords:
            parts.append(
                f"{{\\fs{keyword_font_size}\\1c&H00FFFF&}}{word}{{\\r}}"
            )
        else:
            parts.append(word)

    return " ".join(parts)


def format_ass_time(seconds: float) -> str:
    """Convert seconds to ASS timestamp format H:MM:SS.cc"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
