#!/usr/bin/env python3
"""
Gemini Image Generation Script v3.0 — Nano Banana Pro
通过 Gemini API (gemini-3-pro-image-preview) 生成图片并保存到本地
默认：temperature=1, 1080p分辨率, 宽高比自动
支持：纯文本生成、多参考图合成、迭代编辑
"""

import urllib.request
import urllib.error
import json
import base64
import sys
import os
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

API_KEY = _load_api_key()
MODEL = "gemini-3-pro-image-preview"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/Desktop")

# 默认参数
DEFAULT_TEMPERATURE = 1.0
DEFAULT_IMAGE_SIZE = "1080p"    # 用户默认 1080p；仅 gemini-3-pro-image-preview 支持 imageSize
DEFAULT_ASPECT_RATIO = None     # None = auto（模型自动决定，有参考图时匹配输入）

_1080P_TARGETS = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1":  (1080, 1080),
    "4:3":  (1440, 1080),
    "3:4":  (1080, 1440),
}


def _resolve_image_size(size_str, aspect_ratio=None):
    """将 1080p 解析为 API 接受的 imageSize 值；1K/2K/4K 直接透传
    gemini-3-pro-image-preview 只接受预设值（1K/2K/4K），不接受像素尺寸。
    1080p → 内部用 2K 生成（≥1080p），保存后自动下采样到 1080p。"""
    if size_str and size_str.lower() == "1080p":
        return "2K"  # 2K ≈ 1536x2752 (9:16)，下采样到 1080x1920
    return size_str


def _downscale_to_1080p(filepath, aspect_ratio=None):
    """将图片下采样到 1080p 目标尺寸（PIL LANCZOS）"""
    try:
        from PIL import Image
    except ImportError:
        print("[警告] PIL 未安装，跳过 1080p 下采样")
        return filepath

    target = _1080P_TARGETS.get(aspect_ratio, (1080, 1920))  # 默认 9:16
    img = Image.open(filepath)
    w, h = img.size

    # 只在原图大于目标时才下采样
    if w <= target[0] and h <= target[1]:
        return filepath

    img_resized = img.resize(target, Image.LANCZOS)

    # 保存为 PNG 无损（1080p 文件不大）
    png_path = os.path.splitext(filepath)[0] + ".png"
    img_resized.save(png_path, "PNG")

    # 删除原始大文件
    if png_path != filepath:
        os.remove(filepath)

    print("[1080p] {} → {}x{} ({:.1f} KB)".format(
        os.path.basename(png_path), target[0], target[1],
        os.path.getsize(png_path) / 1024))
    return png_path


def generate_image(
    prompt,                     # type: str
    output_name=None,           # type: Optional[str]
    reference_images=None,      # type: Optional[List[str]]
    output_dir=None,            # type: Optional[str]
    model=None,                 # type: Optional[str]
    temperature=None,           # type: Optional[float]
    aspect_ratio=None,          # type: Optional[str]
    image_size=None             # type: Optional[str]
):
    """
    调用 Gemini API 生成图片

    Args:
        prompt: 英文提示词
        output_name: 输出文件名（不含扩展名），默认用时间戳
        reference_images: 参考图片路径列表（用于多图合成）
        output_dir: 输出目录，默认桌面
        model: 模型名称，默认 gemini-3-pro-image-preview
        temperature: 温度参数，默认 1.0
        aspect_ratio: 宽高比（如 "9:16"），None 为自动
        image_size: 图片分辨率（"1080p"/"1K"/"2K"/"4K"），默认 1080p
    """
    use_model = model or MODEL
    use_dir = output_dir or DEFAULT_OUTPUT_DIR
    use_temp = temperature if temperature is not None else DEFAULT_TEMPERATURE
    use_ratio = aspect_ratio or DEFAULT_ASPECT_RATIO
    raw_size = image_size or DEFAULT_IMAGE_SIZE
    is_1080p = raw_size.lower() == "1080p" if raw_size else False
    use_size = _resolve_image_size(raw_size, use_ratio)
    url = API_URL.format(model=use_model, key=API_KEY)

    os.makedirs(use_dir, exist_ok=True)

    # 构建 parts
    parts = []

    # 如果有参考图片，先加入图片
    if reference_images:
        for i, img_path in enumerate(reference_images):
            img_path = os.path.expanduser(img_path)
            if not os.path.exists(img_path):
                print("[错误] 图片不存在: {}".format(img_path))
                return None

            with open(img_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")

            ext = os.path.splitext(img_path)[1].lower()
            mime_map = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif"
            }
            mime_type = mime_map.get(ext, "image/jpeg")

            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": img_data
                }
            })
            size_kb = len(img_data) * 3 / 4 / 1024
            print("[Image {}] 已加载: {} ({:.0f} KB)".format(
                i + 1, os.path.basename(img_path), size_kb))

    # 加入文本提示词
    parts.append({"text": prompt})

    # 构建 generationConfig
    gen_config = {
        "temperature": use_temp,
        "responseModalities": ["TEXT", "IMAGE"]
    }

    # 构建 imageConfig
    image_config = {}
    if use_ratio:
        image_config["aspectRatio"] = use_ratio
    if use_size and "3-pro" in use_model:
        # imageSize 仅 gemini-3-pro-image-preview 支持
        image_config["imageSize"] = use_size

    if image_config:
        gen_config["imageConfig"] = image_config

    # 构建请求体
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": gen_config
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    # 打印请求信息
    display_size = "1080p(2K→downscale)" if is_1080p else use_size
    config_info = "model={}, temp={}, size={}".format(use_model, use_temp, display_size)
    if use_ratio:
        config_info += ", ratio={}".format(use_ratio)
    else:
        config_info += ", ratio=auto"
    print("\n[请求] 正在调用 Nano Banana Pro API...")
    print("[配置] {}".format(config_info))
    prompt_preview = prompt[:150] + ("..." if len(prompt) > 150 else "")
    print("[提示词] {}".format(prompt_preview))

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print("\n[HTTP 错误] {}: {}".format(e.code, e.reason))
        try:
            err_json = json.loads(error_body)
            msg = err_json.get("error", {}).get("message", "")
            print("[详情] {}".format(msg))
        except Exception:
            print(error_body[:500])
        return None
    except urllib.error.URLError as e:
        print("\n[网络错误] {}".format(e.reason))
        return None
    except Exception as e:
        print("\n[超时/未知错误] {}".format(str(e)))
        return None

    # 解析响应
    if "candidates" not in result:
        print("[错误] 响应中没有 candidates")
        if "promptFeedback" in result:
            feedback = result["promptFeedback"]
            print("[安全过滤] {}".format(json.dumps(feedback, ensure_ascii=False)))
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
        return None

    candidate = result["candidates"][0]

    # 检查是否被安全过滤中断
    finish_reason = candidate.get("finishReason", "")
    if finish_reason == "SAFETY":
        print("[安全过滤] 内容被过滤，请调整提示词")
        safety_ratings = candidate.get("safetyRatings", [])
        for r in safety_ratings:
            if r.get("probability", "NEGLIGIBLE") != "NEGLIGIBLE":
                print("  - {}: {}".format(r.get("category", ""), r.get("probability", "")))
        return None

    content = candidate.get("content", {})
    parts_resp = content.get("parts", [])

    saved_files = []
    text_response = ""
    img_count = 0

    for part in parts_resp:
        if "text" in part:
            text_response = part["text"].strip()
            if text_response:
                print("\n[AI 回复] {}".format(text_response))

        # 兼容 snake_case 和 camelCase
        inline_data = part.get("inline_data") or part.get("inlineData")
        if inline_data:
            img_b64 = inline_data.get("data") or inline_data.get("data", "")
            mime = (inline_data.get("mime_type")
                    or inline_data.get("mimeType", "image/png"))

            ext = ".png"
            if "jpeg" in mime or "jpg" in mime:
                ext = ".jpg"
            elif "webp" in mime:
                ext = ".webp"

            img_count += 1
            if output_name:
                if img_count == 1:
                    filename = "{}{}".format(output_name, ext)
                else:
                    filename = "{}_{}{}".format(output_name, img_count, ext)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = "gemini_{}{}".format(timestamp, ext)

            filepath = os.path.join(use_dir, filename)

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(img_b64))

            file_size = os.path.getsize(filepath) / 1024
            print("\n[已保存] {} ({:.1f} KB)".format(filepath, file_size))

            # 1080p 模式：下采样到目标尺寸
            if is_1080p:
                filepath = _downscale_to_1080p(filepath, use_ratio)

            saved_files.append(filepath)

    if not saved_files:
        print("\n[警告] 响应中没有图片数据")
        if text_response:
            print("[AI 说] {}".format(text_response))

    return saved_files


def main():
    parser = argparse.ArgumentParser(description="Nano Banana Pro Image Generation")
    parser.add_argument("prompt", help="英文提示词")
    parser.add_argument("-n", "--name", help="输出文件名（不含扩展名）")
    parser.add_argument("-o", "--output-dir", help="输出目录")
    parser.add_argument("-r", "--ref", action="append", help="参考图片路径（可多次使用）")
    parser.add_argument("-m", "--model", help="模型名称", default=None)
    parser.add_argument("-t", "--temperature", type=float, help="温度参数", default=None)
    parser.add_argument("-a", "--aspect-ratio", help="宽高比（如 9:16），不指定则自动", default=None)
    parser.add_argument("-s", "--image-size", help="分辨率（1080p/1K/2K/4K），默认 1080p", default=None)
    args = parser.parse_args()

    result = generate_image(
        prompt=args.prompt,
        output_name=args.name,
        reference_images=args.ref,
        output_dir=args.output_dir,
        model=args.model,
        temperature=args.temperature,
        aspect_ratio=args.aspect_ratio,
        image_size=args.image_size
    )

    if result:
        print("\n[完成] 共生成 {} 张图片".format(len(result)))
        sys.exit(0)
    else:
        print("\n[失败] 图片生成失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
