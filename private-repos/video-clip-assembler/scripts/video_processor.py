"""
Video processing: trim, concat, burn subtitles, auto-compress.
Uses ffmpeg via imageio_ffmpeg.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def get_ffmpeg_path():
    """Get ffmpeg path — prefer system ffmpeg, fallback to imageio_ffmpeg."""
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def _run_ffmpeg(cmd):
    """Run ffmpeg command, raise with stderr details on failure."""
    result = subprocess.run(cmd, capture_output=True, timeout=300)
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace")[-500:]
        raise subprocess.CalledProcessError(
            result.returncode, cmd,
            output=result.stdout, stderr=f"ffmpeg error: {stderr}".encode()
        )
    return result


def trim_segment(
    input_path: str,
    start: float,
    end: float,
    output_path: str,
    padding: float = 0.1,
) -> str:
    """Trim a video segment — stream copy first (low memory), re-encode only at concat."""
    ffmpeg = get_ffmpeg_path()

    actual_start = max(0, start - padding)
    actual_end = end + padding
    duration = actual_end - actual_start

    # Step 1: fast stream-copy trim (near-zero memory)
    raw_path = output_path.replace(".mp4", "_raw.mp4")
    cmd_copy = [
        ffmpeg, "-y",
        "-ss", f"{actual_start:.3f}",
        "-i", input_path,
        "-t", f"{duration:.3f}",
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        raw_path
    ]
    try:
        _run_ffmpeg(cmd_copy)
    except subprocess.CalledProcessError:
        # Clean up partial file
        if os.path.exists(raw_path):
            os.unlink(raw_path)
        # Fallback: re-encode with -i before -ss (slower seek but more compatible)
        cmd_encode = [
            ffmpeg, "-y",
            "-i", input_path,
            "-ss", f"{actual_start:.3f}",
            "-t", f"{duration:.3f}",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "20",
            "-r", "30",
            "-vsync", "cfr",
            "-threads", "1",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-ac", "2",
            "-max_muxing_queue_size", "512",
            "-avoid_negative_ts", "make_zero",
            output_path
        ]
        _run_ffmpeg(cmd_encode)
        return output_path

    # Step 2: re-encode the small trimmed clip with normalized audio (concat-ready)
    # Force 30fps CFR to fix iPhone VFR (variable frame rate) issues
    cmd_encode = [
        ffmpeg, "-y",
        "-i", raw_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-r", "30",
        "-vsync", "cfr",
        "-threads", "2",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "2",
        output_path
    ]
    _run_ffmpeg(cmd_encode)

    if os.path.exists(raw_path):
        os.unlink(raw_path)
    return output_path


def concat_segments(segment_paths: list, output_path: str) -> str:
    """Concatenate video segments using concat demuxer (stream copy, no re-encode)."""
    ffmpeg = get_ffmpeg_path()

    # Segments are already normalized by trim_segment — concat via stream copy
    list_path = output_path + ".txt"
    with open(list_path, "w") as f:
        for path in segment_paths:
            safe_path = path.replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")

    cmd = [
        ffmpeg, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True, timeout=300)

    os.unlink(list_path)
    return output_path


def burn_subtitles(input_path: str, ass_path: str, output_path: str, fonts_dir: str = None) -> str:
    """Burn ASS subtitles into video. fonts_dir points to custom font directory."""
    ffmpeg = get_ffmpeg_path()

    safe_ass = ass_path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")

    vf = f"ass={safe_ass}"
    if fonts_dir:
        safe_fonts = fonts_dir.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        vf = f"ass={safe_ass}:fontsdir={safe_fonts}"

    cmd = [
        ffmpeg, "-y",
        "-i", input_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-r", "30",
        "-vsync", "cfr",
        "-threads", "2",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "2",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True, timeout=300)
    return output_path


def compress_to_1080p(input_path: str, output_path: str) -> str:
    """Compress video to 1080p (max 1080 width for vertical, 1920 for horizontal)."""
    ffmpeg = get_ffmpeg_path()

    cmd = [
        ffmpeg, "-y",
        "-i", input_path,
        "-vf", "scale='if(gt(iw,ih),min(1920,iw),-2)':'if(gt(iw,ih),-2,min(1920,ih))'",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True, timeout=300)
    return output_path


def merge_consecutive_segments(selections: list, gap_threshold: float = 1.0) -> list:
    """
    Merge consecutive selections from the same clip into single trim operations.
    Only splits when there's a gap > gap_threshold or a different clip.
    Returns list of merged groups: [{clip_path, start, end, sentences: [...]}, ...]
    """
    if not selections:
        return []

    merged = []
    current = {
        "clip_path": selections[0]["clip_path"],
        "start": selections[0]["start"],
        "end": selections[0]["end"],
        "sentences": [selections[0]],
    }

    for sel in selections[1:]:
        # Same clip and close in time → merge
        if (sel["clip_path"] == current["clip_path"] and
                sel["start"] - current["end"] < gap_threshold):
            current["end"] = sel["end"]
            current["sentences"].append(sel)
        else:
            merged.append(current)
            current = {
                "clip_path": sel["clip_path"],
                "start": sel["start"],
                "end": sel["end"],
                "sentences": [sel],
            }

    merged.append(current)
    return merged


def build_video_phase1(
    selections: list,
    temp_dir: str,
    progress_callback=None,
) -> dict:
    """
    Phase 1: Trim + Concat only.
    Returns {concat_path, subtitle_segments} for phase 2.
    """
    def report(stage, pct, msg):
        if progress_callback:
            progress_callback(stage, pct, msg)

    merged = merge_consecutive_segments(selections)
    total_groups = len(merged)
    total_sents = len(selections)
    padding = 0.1

    report("trimming", 5, f"合并为 {total_groups} 个连续片段（共 {total_sents} 句）...")

    trimmed_paths = []
    running_offset = 0.0
    subtitle_segments = []

    for i, group in enumerate(merged):
        seg_path = os.path.join(temp_dir, f"seg_{i:03d}.mp4")
        report("trimming", 5 + int(i / total_groups * 30), f"裁剪中 ({i+1}/{total_groups})...")
        trim_segment(group["clip_path"], group["start"], group["end"], seg_path)
        trimmed_paths.append(seg_path)

        group_duration = group["end"] - group["start"] + 2 * padding

        for sent in group["sentences"]:
            sub_start = running_offset + padding + (sent["start"] - group["start"])
            sub_end = running_offset + padding + (sent["end"] - group["start"])
            subtitle_segments.append({
                "text": sent["text"],
                "start": sub_start,
                "end": sub_end,
                "words": sent.get("words", []),
            })

        running_offset += group_duration

    report("concat", 40, "拼接片段中...")
    concat_path = os.path.join(temp_dir, "concat.mp4")
    concat_segments(trimmed_paths, concat_path)

    # Cleanup trimmed segments
    for path in trimmed_paths:
        if os.path.exists(path):
            os.unlink(path)

    report("subtitle_choice", 50, "拼接完成，请选择是否添加字幕")
    return {"concat_path": concat_path, "subtitle_segments": subtitle_segments}


def build_video_phase2_subtitle(
    concat_path: str,
    subtitle_segments: list,
    keyword_highlights: dict,
    temp_dir: str,
    output_path: str,
    fonts_dir: str = None,
    progress_callback=None,
    max_size_mb: int = 200,
) -> str:
    """Phase 2 with subtitles: Generate ASS → Burn → Compress."""
    from ass_generator import generate_ass

    def report(stage, pct, msg):
        if progress_callback:
            progress_callback(stage, pct, msg)

    report("subtitle", 55, "生成字幕文件...")
    ass_path = os.path.join(temp_dir, "subtitles.ass")
    generate_ass(subtitle_segments, keyword_highlights, ass_path)

    report("burning", 65, "烧录字幕到视频中...")
    burn_subtitles(concat_path, ass_path, output_path, fonts_dir=fonts_dir)

    # Cleanup concat
    if os.path.exists(concat_path):
        os.unlink(concat_path)

    return _compress_if_needed(output_path, max_size_mb, report)


def build_video_phase2_no_subtitle(
    concat_path: str,
    output_path: str,
    progress_callback=None,
    max_size_mb: int = 200,
) -> str:
    """Phase 2 without subtitles: just rename/compress."""
    def report(stage, pct, msg):
        if progress_callback:
            progress_callback(stage, pct, msg)

    report("burning", 70, "跳过字幕，准备输出...")
    shutil.move(concat_path, output_path)
    return _compress_if_needed(output_path, max_size_mb, report)


def _compress_if_needed(output_path: str, max_size_mb: int, report) -> str:
    """Compress to 1080p if file exceeds max_size_mb."""
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        report("compressing", 85, f"文件 {file_size_mb:.0f}MB 超过 {max_size_mb}MB，压缩到 1080p...")
        compressed_path = output_path.replace(".mp4", "_compressed.mp4")
        compress_to_1080p(output_path, compressed_path)
        os.unlink(output_path)
        shutil.move(compressed_path, output_path)
        new_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        report("compressing", 95, f"压缩完成: {file_size_mb:.0f}MB → {new_size_mb:.0f}MB")

    report("done", 100, "视频生成完成！")
    return output_path
