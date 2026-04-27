#!/usr/bin/env python3
"""
Seedance 1.5 Pro Video Generation Script v1.0
通过火山引擎 Ark API (doubao-seedance-1-5-pro-251215) 生成视频并保存到本地
异步模式：提交 → 轮询 → 下载
支持：文生视频、图生视频（首帧/首尾帧）、草稿预览
默认：9:16, 720p, 5s, 带音频
"""

import urllib.request
import urllib.error
import json
import base64
import sys
import os
import time
import argparse
from datetime import datetime


API_KEY = "fc882ab9-bc70-4999-8a7a-df978795cf3b"
MODEL = "doubao-seedance-1-5-pro-251215"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/Desktop")

# 默认参数
DEFAULT_RATIO = "9:16"
DEFAULT_RESOLUTION = "720p"
DEFAULT_DURATION = 5
DEFAULT_GENERATE_AUDIO = True

# 轮询参数
POLL_INTERVAL = 10            # 秒
MAX_POLL_ATTEMPTS = 120       # 最多轮询 120 次 = 20 分钟

# ============================================================
# 计费器（官方火山方舟定价）
# Token 公式：width × height × fps × duration / 1024
# ============================================================
_PRICE_WITH_AUDIO = 16.8     # 元/百万 tokens（带音频）
_PRICE_NO_AUDIO   = 8.4      # 元/百万 tokens（静音）
_DEFAULT_FPS      = 24

# 各分辨率标准像素数（以 16:9 为基准；9:16 像素数相同）
_RES_PIXELS = {
    "480p":  854  * 480,    # 409,920
    "720p":  1280 * 720,    # 921,600
    "1080p": 1920 * 1080,   # 2,073,600
}

# 本次会话累计消耗
_session_tokens = 0
_session_cost   = 0.0

# 持久化日志文件（跨会话累计）
COST_LOG = os.path.expanduser("~/Desktop/seedance_cost_log.jsonl")


def _estimate_cost(resolution, duration, generate_audio, fps=_DEFAULT_FPS):
    """根据参数估算 token 数和费用（返回 tokens, 元）"""
    pixels = _RES_PIXELS.get(resolution, _RES_PIXELS["720p"])
    tokens = pixels * fps * duration / 1024
    price  = _PRICE_WITH_AUDIO if generate_audio else _PRICE_NO_AUDIO
    cost   = tokens * price / 1_000_000
    return int(tokens), cost


def _actual_cost(total_tokens, generate_audio):
    """根据实际 token 数计算费用（元）"""
    price = _PRICE_WITH_AUDIO if generate_audio else _PRICE_NO_AUDIO
    return total_tokens * price / 1_000_000


def _log_cost(tokens, cost, resolution, duration, generate_audio):
    """追加写入桌面日志（每次生成后调用）"""
    record = {
        "ts":         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tokens":     tokens,
        "cost":       round(cost, 6),
        "resolution": resolution,
        "duration":   duration,
        "audio":      generate_audio,
    }
    try:
        with open(COST_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass  # 日志写失败不影响主流程


def _print_cost_summary():
    """打印本次会话累计费用"""
    if _session_tokens > 0:
        print("\n[会话累计] {:,} tokens | ¥{:.4f}".format(_session_tokens, _session_cost))


def _api_request(url, data=None, method="GET"):
    """发送 API 请求"""
    headers = {
        "Authorization": "Bearer {}".format(API_KEY),
        "Content-Type": "application/json"
    }

    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(error_body)
            # Ark API 错误格式
            err_obj = err_json.get("error", {})
            msg = err_obj.get("message", error_body[:300])
            code = err_obj.get("code", "")
            if code:
                msg = "{}: {}".format(code, msg)
        except Exception:
            msg = error_body[:300]
        return None, "HTTP {}: {}".format(e.code, msg)
    except urllib.error.URLError as e:
        return None, "网络错误: {}".format(e.reason)
    except Exception as e:
        return None, "未知错误: {}".format(str(e))


def _image_to_data_url(image_path, optimize_payload=False):
    """读取本地图片并转为 data URL。

    optimize_payload=True 时，PNG 会转为 JPEG q=98（subsampling=0）以减小 base64 体积，
    避免双帧模式下 payload 过大导致服务端超时。原始文件不受影响。
    """
    path = os.path.expanduser(image_path)
    if not os.path.exists(path):
        print("[错误] 图片不存在: {}".format(path))
        return None

    size_mb = os.path.getsize(path) / (1024 * 1024)
    if size_mb > 30:
        print("[错误] 图片超过 30MB 限制: {:.1f}MB".format(size_mb))
        return None

    ext = os.path.splitext(path)[1].lower()

    # 双帧模式下 PNG 转 JPEG q=98 减小 payload（原文件不变）
    if optimize_payload and ext == ".png":
        try:
            from PIL import Image
            import io
            img = Image.open(path)
            if img.mode == "RGBA":
                img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=98, subsampling=0)
            raw_bytes = buf.getvalue()
            mime_type = "image/jpeg"
            new_kb = len(raw_bytes) / 1024
            print("[图片] {} PNG→JPEG q=98: {:.0f}KB → {:.0f}KB（原文件不变）".format(
                os.path.basename(path), size_mb * 1024, new_kb))
        except ImportError:
            print("[警告] PIL 未安装，跳过 payload 优化，直传原始 PNG")
            with open(path, "rb") as f:
                raw_bytes = f.read()
            mime_type = "image/png"
    else:
        with open(path, "rb") as f:
            raw_bytes = f.read()
        mime_map = {
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp", ".bmp": "image/bmp", ".tiff": "image/tiff",
            ".gif": "image/gif", ".heic": "image/heic", ".heif": "image/heif"
        }
        mime_type = mime_map.get(ext, "image/jpeg")

    raw_b64 = base64.b64encode(raw_bytes).decode("utf-8")
    b64_mb = len(raw_b64) / (1024 * 1024)
    print("[图片] 已加载: {} ({:.1f} MB, base64 {:.1f} MB)".format(
        os.path.basename(path), len(raw_bytes) / (1024 * 1024), b64_mb))
    return "data:{};base64,{}".format(mime_type, raw_b64)


def generate_video(
    prompt,
    output_name=None,
    output_dir=None,
    duration=None,
    ratio=None,
    resolution=None,
    generate_audio=None,
    camera_fixed=False,
    watermark=False,
    first_frame=None,
    last_frame=None,
    audio_ref=None,
    draft=False,
    seed=-1,
    return_last_frame=False
):
    """
    调用 Seedance 1.5 Pro API 生成视频

    Args:
        prompt: 视频描述提示词（中文或英文）
        output_name: 输出文件名（不含扩展名）
        output_dir: 输出目录
        duration: 视频时长（4-12秒），-1 自动
        ratio: 宽高比（9:16/16:9/4:3/3:4/1:1/21:9/adaptive）
        resolution: 分辨率（480p/720p/1080p）
        generate_audio: 是否生成音频
        camera_fixed: 是否固定镜头
        watermark: 是否加水印
        first_frame: 首帧图片路径（图生视频）
        last_frame: 尾帧图片路径（首尾帧模式）
        draft: 草稿模式（480p 预览，低消耗）
        seed: 随机种子（-1 随机）
        return_last_frame: 是否返回最后一帧 PNG
    """
    use_dir = output_dir or DEFAULT_OUTPUT_DIR
    use_duration = duration if duration is not None else DEFAULT_DURATION
    use_ratio = ratio or DEFAULT_RATIO
    use_resolution = resolution or DEFAULT_RESOLUTION
    use_audio = generate_audio if generate_audio is not None else DEFAULT_GENERATE_AUDIO

    os.makedirs(use_dir, exist_ok=True)

    # 草稿模式约束
    if draft:
        use_resolution = "480p"
        print("[草稿模式] 分辨率强制为 480p")

    # 构建 content 数组
    content = [{"type": "text", "text": prompt}]

    # 双帧模式检测：两张本地图片时自动优化 payload（PNG→JPEG q=98）
    is_dual_local = (first_frame and last_frame and
                     not first_frame.startswith("http") and
                     not last_frame.startswith("http"))
    if is_dual_local:
        print("[双帧模式] 检测到首帧+尾帧均为本地文件，PNG 将自动转为 JPEG q=98 以避免 payload 超时")

    # 首帧图片
    if first_frame:
        if first_frame.startswith("http"):
            img_url = first_frame
        else:
            img_url = _image_to_data_url(first_frame, optimize_payload=is_dual_local)
            if not img_url:
                return None
        content.append({
            "type": "image_url",
            "image_url": {"url": img_url},
            "role": "first_frame"
        })
        # 图生视频默认用 adaptive 比例
        if ratio is None:
            use_ratio = "adaptive"

    # 尾帧图片
    if last_frame:
        if last_frame.startswith("http"):
            img_url = last_frame
        else:
            img_url = _image_to_data_url(last_frame, optimize_payload=is_dual_local)
            if not img_url:
                return None
        content.append({
            "type": "image_url",
            "image_url": {"url": img_url},
            "role": "last_frame"
        })

    # 音频参考
    if audio_ref:
        if audio_ref.startswith("http") or audio_ref.startswith("data:"):
            audio_url = audio_ref
        else:
            # 本地文件转 base64 data URL
            ext = os.path.splitext(audio_ref)[1].lower()
            mime_map = {".wav": "audio/wav", ".mp3": "audio/mpeg", ".m4a": "audio/mp4",
                        ".ogg": "audio/ogg", ".flac": "audio/flac", ".aac": "audio/aac"}
            mime = mime_map.get(ext, "audio/wav")
            with open(audio_ref, "rb") as af:
                audio_b64 = base64.b64encode(af.read()).decode()
            audio_url = "data:{};base64,{}".format(mime, audio_b64)
            fsize = os.path.getsize(audio_ref)
            print("[音频] 已加载: {} ({:.1f} KB)".format(os.path.basename(audio_ref), fsize / 1024))
        content.append({
            "type": "audio_url",
            "audio_url": {"url": audio_url},
            "role": "reference_audio"
        })

    # 构建请求体
    payload = {
        "model": MODEL,
        "content": content,
        "ratio": use_ratio,
        "resolution": use_resolution,
        "duration": use_duration,
        "generate_audio": use_audio,
        "camera_fixed": camera_fixed,
        "watermark": watermark,
        "draft": draft,
        "seed": seed
    }

    if return_last_frame:
        payload["return_last_frame"] = True

    # 打印请求信息
    mode = "草稿" if draft else ("首尾帧" if last_frame else ("图生视频" if first_frame else "文生视频"))
    print("\n" + "=" * 60)
    print("[Seedance 1.5 Pro] 视频生成")
    print("=" * 60)
    print("[配置] 时长={}s | 比例={} | 分辨率={} | 音频={} | 模式={}".format(
        use_duration, use_ratio, use_resolution, "开" if use_audio else "关", mode))
    prompt_preview = prompt[:120] + ("..." if len(prompt) > 120 else "")
    print("[提示词] {}".format(prompt_preview))

    # 预估费用
    est_tokens, est_cost = _estimate_cost(use_resolution, use_duration, use_audio)
    print("[预估费用] ~{:,} tokens ≈ ¥{:.4f}（{}）".format(
        est_tokens, est_cost, "带音频" if use_audio else "静音"))

    # ========== 步骤 1：提交请求 ==========
    print("\n[步骤1] 提交视频生成请求...")
    result, err = _api_request(BASE_URL, data=payload, method="POST")
    if err:
        print("[错误] 提交失败: {}".format(err))
        return None

    task_id = result.get("id")
    if not task_id:
        print("[错误] 响应中没有 task id")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
        return None

    print("[成功] 任务已提交: {}".format(task_id))

    # ========== 步骤 2：轮询状态 ==========
    print("\n[步骤2] 等待视频生成（每{}秒检查一次）...".format(POLL_INTERVAL))
    poll_url = "{}/{}".format(BASE_URL, task_id)

    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        time.sleep(POLL_INTERVAL)

        status_result, err = _api_request(poll_url, method="GET")
        if err:
            print("[轮询 {}/{}] 查询失败: {}，继续等待...".format(attempt, MAX_POLL_ATTEMPTS, err))
            continue

        status = status_result.get("status", "unknown")
        elapsed = attempt * POLL_INTERVAL
        mins = elapsed // 60
        secs = elapsed % 60

        if status == "succeeded":
            time_str = "{}分{}秒".format(mins, secs) if mins > 0 else "{}秒".format(secs)
            print("[轮询 {}/{}] 生成完成！(耗时约{})".format(attempt, MAX_POLL_ATTEMPTS, time_str))
            break
        elif status in ("failed", "cancelled", "expired"):
            error_info = status_result.get("error", {})
            print("[失败] 状态: {} | 错误: {}".format(status, json.dumps(error_info, ensure_ascii=False)))
            return None
        else:
            time_str = "{}分{}秒".format(mins, secs) if mins > 0 else "{}秒".format(secs)
            print("[轮询 {}/{}] {} (已等待{})".format(attempt, MAX_POLL_ATTEMPTS, status, time_str))
    else:
        print("\n[超时] 超过最大等待时间（{}分钟）".format(MAX_POLL_ATTEMPTS * POLL_INTERVAL // 60))
        print("[任务ID] {} （可稍后手动查询）".format(task_id))
        return None

    # ========== 步骤 3：下载视频 ==========
    print("\n[步骤3] 下载视频...")

    content_data = status_result.get("content", {})
    video_url = content_data.get("video_url", "")

    if not video_url:
        print("[错误] 响应中没有视频 URL")
        print("[调试] {}".format(json.dumps(status_result, indent=2, ensure_ascii=False)[:800]))
        return None

    # 构建文件名
    if output_name:
        filename = "{}.mp4".format(output_name)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "seedance_{}.mp4".format(timestamp)

    filepath = os.path.join(use_dir, filename)

    print("[下载] → {}".format(filename))

    try:
        dl_req = urllib.request.Request(video_url)
        with urllib.request.urlopen(dl_req, timeout=300) as resp:
            video_data = resp.read()

        with open(filepath, "wb") as f:
            f.write(video_data)

        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print("[已保存] {} ({:.1f} MB)".format(filepath, file_size_mb))

    except Exception as e:
        print("[下载失败] {}".format(str(e)))
        print("[视频URL] {} （24小时内有效，请手动下载）".format(video_url))
        return None

    # 下载最后一帧（如果请求了）
    last_frame_url = content_data.get("last_frame_url", "")
    if last_frame_url and return_last_frame:
        frame_path = os.path.join(use_dir, "{}_lastframe.png".format(output_name or "seedance"))
        try:
            with urllib.request.urlopen(last_frame_url, timeout=60) as resp:
                with open(frame_path, "wb") as f:
                    f.write(resp.read())
            print("[最后一帧] {}".format(frame_path))
        except Exception as e:
            print("[最后一帧下载失败] {}".format(str(e)))

    # 打印使用信息 + 实际费用
    global _session_tokens, _session_cost
    usage = status_result.get("usage", {})
    if usage:
        tokens = usage.get("total_tokens", 0)
        real_cost = _actual_cost(tokens, use_audio)
        _session_tokens += tokens
        _session_cost   += real_cost
        _log_cost(tokens, real_cost, use_resolution, use_duration, use_audio)
        print("[实际消耗] {:,} tokens | ¥{:.4f}（{}）| 本次会话累计 ¥{:.4f}".format(
            tokens, real_cost, "带音频" if use_audio else "静音", _session_cost))

    actual_duration = status_result.get("duration", use_duration)
    actual_fps = status_result.get("framespersecond", 24)

    print("\n" + "=" * 60)
    print("[完成] 视频已生成")
    print("  → {}".format(filepath))
    print("  → 时长: {}s | {}fps | {}".format(actual_duration, actual_fps, use_resolution))
    print("=" * 60)

    return [filepath]


def main():
    parser = argparse.ArgumentParser(description="Seedance 1.5 Pro Video Generation")
    parser.add_argument("prompt", help="视频描述提示词（中文或英文）")
    parser.add_argument("-n", "--name", help="输出文件名（不含扩展名）")
    parser.add_argument("-o", "--output-dir", help="输出目录", default=None)
    parser.add_argument("-d", "--duration", type=int,
                        help="视频时长（4-12秒，-1自动）", default=None)
    parser.add_argument("-a", "--ratio",
                        choices=["9:16", "16:9", "4:3", "3:4", "1:1", "21:9", "adaptive"],
                        help="宽高比", default=None)
    parser.add_argument("-r", "--resolution", choices=["480p", "720p", "1080p"],
                        help="分辨率", default=None)
    parser.add_argument("--audio", dest="generate_audio", action="store_true", default=None,
                        help="开启音频生成（默认）")
    parser.add_argument("--no-audio", dest="generate_audio", action="store_false",
                        help="关闭音频生成（静音视频）")
    parser.add_argument("--camera-fixed", action="store_true", default=False,
                        help="固定镜头")
    parser.add_argument("--watermark", action="store_true", default=False,
                        help="添加水印")
    parser.add_argument("-i", "--first-frame", help="首帧图片路径或URL", default=None)
    parser.add_argument("--last-frame", help="尾帧图片路径或URL", default=None)
    parser.add_argument("--audio-ref", help="音频参考文件路径（wav/mp3/m4a）", default=None)
    parser.add_argument("--draft", action="store_true", default=False,
                        help="草稿模式（480p低消耗预览）")
    parser.add_argument("--seed", type=int, default=-1,
                        help="随机种子（-1随机）")
    parser.add_argument("--return-last-frame", action="store_true", default=False,
                        help="返回最后一帧PNG（用于视频衔接）")

    args = parser.parse_args()

    result = generate_video(
        prompt=args.prompt,
        output_name=args.name,
        output_dir=args.output_dir,
        duration=args.duration,
        ratio=args.ratio,
        resolution=args.resolution,
        generate_audio=args.generate_audio,
        camera_fixed=args.camera_fixed,
        watermark=args.watermark,
        first_frame=args.first_frame,
        last_frame=args.last_frame,
        audio_ref=args.audio_ref,
        draft=args.draft,
        seed=args.seed,
        return_last_frame=args.return_last_frame
    )

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
