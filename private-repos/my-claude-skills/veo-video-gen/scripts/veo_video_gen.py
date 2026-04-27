#!/usr/bin/env python3
"""
Veo 3.1 Video Generation Script v2.0
通过 Gemini API (veo-3.1-generate-preview) 生成视频并保存到本地
异步模式：提交 → 轮询 → 下载
支持：纯文本生成、参考图片（image-to-video）、人物参考（referenceImages）
默认：9:16, 4K, 1个视频
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
from typing import Optional, List


def _load_api_key():
    """读取 API Key：优先环境变量，fallback 读 ~/.config/gemini_api_key"""
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        config_path = os.path.expanduser("~/.config/gemini_api_key")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                key = f.read().strip()
    if not key:
        print("[错误] 未找到 GEMINI_API_KEY。请设置环境变量或将 key 写入 ~/.config/gemini_api_key")
        sys.exit(1)
    return key

API_KEY_SUBMIT = _load_api_key()
API_KEY_POLL = API_KEY_SUBMIT
MODEL = "veo-3.1-generate-preview"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
SUBMIT_URL = "{base}/models/{model}:predictLongRunning".format(base=BASE_URL, model=MODEL)
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/Desktop")

# 默认参数
DEFAULT_ASPECT_RATIO = "9:16"
DEFAULT_RESOLUTION = "4k"
DEFAULT_DURATION = 8          # 秒（4K 必须为 8）
DEFAULT_NUM_VIDEOS = 1
DEFAULT_PERSON_GENERATION = "allow_adult"

# 轮询参数
POLL_INTERVAL = 15            # 秒
MAX_POLL_ATTEMPTS = 60        # 最多轮询 60 次 = 15 分钟


def _api_request(url, data=None, method="GET", use_submit_key=False):
    """发送 API 请求"""
    api_key = API_KEY_SUBMIT if use_submit_key else API_KEY_POLL
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }

    if data is not None:
        body = json.dumps(data).encode("utf-8")
    else:
        body = None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(error_body)
            msg = err_json.get("error", {}).get("message", error_body[:300])
        except Exception:
            msg = error_body[:300]
        return None, "HTTP {}: {}".format(e.code, msg)
    except urllib.error.URLError as e:
        return None, "网络错误: {}".format(e.reason)
    except Exception as e:
        return None, "未知错误: {}".format(str(e))


def _load_image_base64(image_path):
    """读取图片并返回 base64 编码和 MIME 类型"""
    path = os.path.expanduser(image_path)
    if not os.path.exists(path):
        print("[错误] 图片不存在: {}".format(path))
        return None, None

    ext = os.path.splitext(path)[1].lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif"
    }
    mime_type = mime_map.get(ext, "image/jpeg")

    with open(path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode("utf-8")

    size_kb = len(img_data) * 3 / 4 / 1024
    print("[图片] 已加载: {} ({:.0f} KB)".format(os.path.basename(path), size_kb))
    return img_data, mime_type


def generate_video(
    prompt,                         # type: str
    output_name=None,               # type: Optional[str]
    output_dir=None,                # type: Optional[str]
    duration=None,                  # type: Optional[int]
    aspect_ratio=None,              # type: Optional[str]
    resolution=None,                # type: Optional[str]
    num_videos=None,                # type: Optional[int]
    negative_prompt=None,           # type: Optional[str]
    image=None,                     # type: Optional[str]
    last_image=None,                # type: Optional[str]
    reference_images=None,          # type: Optional[List[str]]
    model=None                      # type: Optional[str]
):
    """
    调用 Veo 3.1 API 生成视频

    Args:
        prompt: 英文视频描述
        output_name: 输出文件名（不含扩展名）
        output_dir: 输出目录
        duration: 视频时长（4/6/8 秒）
        aspect_ratio: 宽高比（9:16 或 16:9）
        resolution: 分辨率（720p/1080p/4k）
        num_videos: 生成数量（1-4）
        negative_prompt: 负面提示词
        image: 起始帧图片路径（image-to-video）
        last_image: 尾帧图片路径（首尾帧模式，必须配合 image 使用，720p 支持 4/6/8 秒）
        reference_images: 参考图片路径列表（最多3张，用于人物/资产一致性）
    """
    use_dir = output_dir or DEFAULT_OUTPUT_DIR
    use_duration = duration or DEFAULT_DURATION
    use_ratio = aspect_ratio or DEFAULT_ASPECT_RATIO
    use_resolution = resolution or DEFAULT_RESOLUTION
    use_num = num_videos or DEFAULT_NUM_VIDEOS
    use_model = model or MODEL

    # 根据模型重构提交 URL
    submit_url = "{base}/models/{model}:predictLongRunning".format(base=BASE_URL, model=use_model)

    os.makedirs(use_dir, exist_ok=True)

    # 4K 约束检查
    if use_resolution in ("4k", "4K", "1080p") and use_duration != 8:
        print("[警告] {}分辨率仅支持8秒时长，已自动调整为8秒".format(use_resolution))
        use_duration = 8

    # 构建请求体
    parameters = {
        "aspectRatio": use_ratio,
        "resolution": use_resolution,
        "durationSeconds": int(use_duration)  # API 要求整数类型，如 4 而非字符串 "4"
    }

    if negative_prompt:
        parameters["negativePrompt"] = negative_prompt

    # personGeneration: 图生视频/首尾帧用 allow_adult，文生视频用 allow_all
    if image:
        parameters["personGeneration"] = "allow_adult"
    else:
        parameters["personGeneration"] = "allow_all"

    # 构建 instance
    instance = {"prompt": prompt}


    # 如果有起始帧图片（image-to-video）
    if image:
        img_data, mime_type = _load_image_base64(image)
        if img_data:
            instance["image"] = {
                "bytesBase64Encoded": img_data,
                "mimeType": mime_type
            }
            if last_image:
                print("[模式] 首尾帧视频（image + lastFrame）")
            else:
                print("[模式] 图生视频（起始帧）")

    # 如果有尾帧图片（首尾帧模式）
    if last_image:
        last_data, last_mime = _load_image_base64(last_image)
        if last_data:
            instance["lastFrame"] = {
                "bytesBase64Encoded": last_data,
                "mimeType": last_mime
            }

    # 如果有参考图片（人物/资产一致性）
    if reference_images:
        ref_list = []
        for ref_path in reference_images:
            img_data, mime_type = _load_image_base64(ref_path)
            if img_data:
                ref_list.append({
                    "image": {
                        "bytesBase64Encoded": img_data,
                        "mimeType": mime_type
                    },
                    "referenceType": "asset"
                })
        if ref_list:
            parameters["referenceImages"] = ref_list
            print("[模式] 参考图片 x{}（资产一致性）".format(len(ref_list)))

    payload = {
        "instances": [instance],
        "parameters": parameters
    }

    # 打印请求信息
    print("\n" + "=" * 60)
    print("[Veo 3.1] 视频生成")
    print("=" * 60)
    if image and last_image:
        mode = "首尾帧视频"
    elif image:
        mode = "图生视频"
    elif reference_images:
        mode = "参考图"
    else:
        mode = "文生视频"
    print("[配置] 时长={}s | 比例={} | 分辨率={} | 模式={}".format(
        use_duration, use_ratio, use_resolution, mode))
    prompt_preview = prompt[:120] + ("..." if len(prompt) > 120 else "")
    print("[提示词] {}".format(prompt_preview))

    # ========== 步骤 1：提交请求 ==========
    print("[模型] {}".format(use_model))
    print("\n[步骤1] 提交视频生成请求...")
    result, err = _api_request(submit_url, data=payload, method="POST", use_submit_key=True)
    if err:
        print("[错误] 提交失败: {}".format(err))
        return None

    operation_name = result.get("name")
    if not operation_name:
        print("[错误] 响应中没有 operation name")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
        return None

    print("[成功] 任务已提交: {}".format(operation_name))

    # ========== 步骤 2：轮询状态 ==========
    print("\n[步骤2] 等待视频生成（每{}秒检查一次）...".format(POLL_INTERVAL))
    poll_url = "{base}/{op}".format(base=BASE_URL, op=operation_name)

    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        time.sleep(POLL_INTERVAL)

        status_result, err = _api_request(poll_url, method="GET")
        if err:
            print("[轮询 {}/{}] 查询失败: {}，继续等待...".format(attempt, MAX_POLL_ATTEMPTS, err))
            continue

        is_done = status_result.get("done", False)
        elapsed = attempt * POLL_INTERVAL

        if is_done:
            print("[轮询 {}/{}] 生成完成！(耗时约{}秒)".format(attempt, MAX_POLL_ATTEMPTS, elapsed))
            break
        else:
            # 显示进度
            mins = elapsed // 60
            secs = elapsed % 60
            if mins > 0:
                print("[轮询 {}/{}] 生成中... (已等待{}分{}秒)".format(
                    attempt, MAX_POLL_ATTEMPTS, mins, secs))
            else:
                print("[轮询 {}/{}] 生成中... (已等待{}秒)".format(
                    attempt, MAX_POLL_ATTEMPTS, elapsed))
    else:
        print("\n[超时] 超过最大等待时间（{}分钟），任务可能仍在运行".format(
            MAX_POLL_ATTEMPTS * POLL_INTERVAL // 60))
        print("[任务ID] {}".format(operation_name))
        return None

    # ========== 步骤 3：下载视频 ==========
    print("\n[步骤3] 下载视频...")

    # 解析响应中的视频 URI
    response_data = status_result.get("response", {})
    video_response = response_data.get("generateVideoResponse", {})
    samples = video_response.get("generatedSamples", [])

    if not samples:
        print("[错误] 响应中没有视频数据")
        # 检查是否有错误信息
        error_info = status_result.get("error")
        if error_info:
            print("[详情] {}".format(json.dumps(error_info, ensure_ascii=False)))
        else:
            print("[调试] {}".format(json.dumps(status_result, indent=2, ensure_ascii=False)[:800]))
        return None

    saved_files = []
    for i, sample in enumerate(samples):
        video_info = sample.get("video", {})
        video_uri = video_info.get("uri", "")

        if not video_uri:
            print("[警告] 第{}个视频没有 URI，跳过".format(i + 1))
            continue

        # 构建文件名
        if output_name:
            if len(samples) == 1:
                filename = "{}.mp4".format(output_name)
            else:
                filename = "{}_{}.mp4".format(output_name, i + 1)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = "veo_{}.mp4".format(timestamp)

        filepath = os.path.join(use_dir, filename)

        # 下载视频（通过 header 传递 API Key）
        print("[下载] 视频 {} → {}".format(i + 1, filename))

        try:
            dl_req = urllib.request.Request(
                video_uri,
                headers={"x-goog-api-key": API_KEY_POLL}
            )
            with urllib.request.urlopen(dl_req, timeout=300) as resp:
                video_data = resp.read()

            with open(filepath, "wb") as f:
                f.write(video_data)

            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print("[已保存] {} ({:.1f} MB)".format(filepath, file_size_mb))
            saved_files.append(filepath)

        except Exception as e:
            print("[下载失败] {}".format(str(e)))
            # 保存 URI 以便手动下载
            print("[视频URI] {}".format(video_uri))

    if saved_files:
        print("\n" + "=" * 60)
        print("[完成] 共生成 {} 个视频".format(len(saved_files)))
        for f in saved_files:
            print("  → {}".format(f))
        print("=" * 60)
    else:
        print("\n[失败] 没有成功下载任何视频")

    return saved_files


def main():
    parser = argparse.ArgumentParser(description="Veo 3.1 Video Generation")
    parser.add_argument("prompt", help="英文视频描述提示词")
    parser.add_argument("-n", "--name", help="输出文件名（不含扩展名）")
    parser.add_argument("-o", "--output-dir", help="输出目录", default=None)
    parser.add_argument("-d", "--duration", type=int, choices=[4, 6, 8],
                        help="视频时长（秒），4K时固定为8", default=None)
    parser.add_argument("-a", "--aspect-ratio", choices=["9:16", "16:9"],
                        help="宽高比", default=None)
    parser.add_argument("-r", "--resolution", choices=["720p", "1080p", "4k"],
                        help="分辨率", default=None)
    parser.add_argument("--num-videos", type=int, choices=[1, 2, 3, 4],
                        help="生成数量", default=None)
    parser.add_argument("--negative-prompt", help="负面提示词", default=None)
    parser.add_argument("-i", "--image", help="起始帧图片路径（图生视频）", default=None)
    parser.add_argument("-l", "--last-image", help="尾帧图片路径（首尾帧模式，配合 -i 使用）", default=None)
    parser.add_argument("--ref", action="append", help="参考图片路径（可多次使用，最多3张）", default=None)
    parser.add_argument("--model", help="模型名称（如 veo-3.1-lite-generate-preview）", default=None)
    args = parser.parse_args()

    result = generate_video(
        prompt=args.prompt,
        output_name=args.name,
        output_dir=args.output_dir,
        duration=args.duration,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        num_videos=args.num_videos,
        negative_prompt=args.negative_prompt,
        image=args.image,
        last_image=args.last_image,
        reference_images=args.ref,
        model=args.model
    )

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
