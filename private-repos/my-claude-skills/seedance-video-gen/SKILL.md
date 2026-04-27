# Seedance 1.5 Pro 视频生成 Skill

## 概述

通过火山引擎 Ark API 调用豆包 Seedance 1.5 Pro 模型生成视频。
异步模式：提交任务 → 轮询状态 → 下载视频。

## 脚本路径

`~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py`

## 调用方式

```bash
# 不需要 venv，使用系统 Python3 即可
python3 ~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py [参数] "提示词"
```

## 参数速查

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `prompt` | 提示词（位置参数） | 必填 | 中文或英文 |
| `-n` | 输出文件名（不含.mp4） | 自动时间戳 | |
| `-o` | 输出目录 | ~/Desktop | |
| `-d` | 时长（秒） | 5 | 4-12 或 -1(自动) |
| `-a` | 宽高比 | 9:16 | 9:16/16:9/4:3/3:4/1:1/21:9/adaptive |
| `-r` | 分辨率 | 720p | 480p/720p/1080p |
| `--audio` | 开启音频 | 默认开启 | |
| `--no-audio` | 关闭音频（静音） | | |
| `--camera-fixed` | 固定镜头 | 关 | |
| `--watermark` | 加水印 | 关 | |
| `-i` | 首帧图片（路径或URL） | | 图生视频 |
| `--last-frame` | 尾帧图片 | | 首尾帧模式 |
| `--draft` | 草稿预览（480p低消耗） | 关 | |
| `--seed` | 随机种子 | -1(随机) | |
| `--return-last-frame` | 返回最后一帧PNG | 关 | 用于视频衔接 |

## 示例

### 文生视频（带音频）
```bash
python3 ~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py \
  -r 1080p -a '9:16' -d 8 -n test_video \
  '写实风格，一个印尼女生对着手机镜头说："你的面膜敢查BPOM吗？"，自然室内光，TikTok自拍角度'
```

### 静音视频（产品展示类）
```bash
python3 ~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py \
  -r 1080p -a '9:16' -d 5 --no-audio -n product_demo \
  '特写镜头，手持银色管状面膜产品，桌面自然光'
```

### 图生视频（首帧）
```bash
python3 ~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py \
  -r 720p -a adaptive -d 5 \
  -i ~/Desktop/first_frame.jpg \
  -n img2vid_test \
  '女孩微笑着转头看向镜头'
```

### 草稿预览（低消耗试看）
```bash
python3 ~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py \
  --draft -d 5 -n draft_preview \
  '测试提示词内容'
```

## Seedance 2.0（doubao-seedance-2-0-260128）

**2.0 的 API 参数和 1.5 Pro 完全不同，不能混用。**

### 关键区别

| | 1.5 Pro | 2.0 |
|--|---------|-----|
| 模型名 | `doubao-seedance-1-5-pro-251215` | `doubao-seedance-2-0-260128` |
| 时长 | 4-12秒 | 4-15秒 |
| 宽高比参数名 | `video_ratio`（嵌套在 `parameters` 里） | **`ratio`**（顶层） |
| 时长参数名 | `video_duration`（嵌套在 `parameters` 里） | **`duration`**（顶层） |
| 分辨率参数名 | `resolution`（嵌套在 `parameters` 里） | **`resolution`**（顶层） |
| 参数位置 | 嵌套在 `parameters: {}` 对象内 | **全部在请求体顶层** |

### 2.0 正确的请求体格式

```json
{
  "model": "doubao-seedance-2-0-260128",
  "content": [
    {"type": "text", "text": "提示词"},
    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
  ],
  "ratio": "9:16",
  "duration": 15,
  "resolution": "720p",
  "generate_audio": false,
  "watermark": false,
  "negative_prompt": "..."
}
```

### 2.0 踩坑记录

- 如果用 1.5 Pro 的嵌套格式（`parameters: {video_ratio, video_duration}`），**参数会被静默忽略**，输出默认 5 秒 1:1
- 真人面部参考图会触发 `PrivacyInformation` 安全策略 → 用无人脸分镜图或纯文生视频
- 图生视频模式下 duration 参数是否生效需实测（2026-04-27 实测：用顶层 `duration: 15` 成功出 15 秒）

---

## 与 Veo 的对比

| 特性 | Seedance 1.5 Pro | Veo 3.1 |
|------|-----------------|---------|
| 时长 | 4-12秒（任意整数） | 4/6/8秒 |
| 音频 | 原生支持（语音+音效+BGM） | 有语音但不可精确控制 |
| 提示词语言 | 中文+英文 | 仅英文 |
| 分辨率 | 480p/720p/1080p | 720p/1080p/4K |
| 宽高比 | 7种+adaptive | 2种（9:16/16:9） |
| 图生视频 | 首帧/尾帧/首尾帧 | 仅首帧 |
| 草稿模式 | 有（480p低消耗） | 无 |
| 镜头固定 | camera_fixed 参数 | 仅靠 negative prompt |
| 台词控制 | 双引号对话，支持多语种 | 无法精确控制 |
| 视频衔接 | return_last_frame | 无 |
| 输出 | MP4 24fps | MP4 24fps |

## 适用场景建议

- **口播视频**（有台词）→ Seedance（原生音频+台词控制更强）
- **产品展示**（静物/手持）→ 即梦 或 Seedance（--no-audio）
- **人物场景**（无特定台词）→ Veo 或 Seedance
- **需要超高分辨率（4K）**→ Veo（Seedance 最高 1080p）

## API 限制

- 视频 URL **24小时内有效**，必须及时下载
- 任务记录保留 **7天**
- 图片输入：jpeg/png/webp/bmp/tiff/gif/heic，最大 30MB，宽高 300-6000px
- 真人面部图片可能触发隐私安全检测
- 提示词建议：中文 <500字，英文 <1000词
- 台词写法：用双引号包裹，如 `女孩说："你好"`
- 多人对话需明确标注每人特征（性别/年龄/服装）
- `reference_audio` 文档声称支持但 1.5 Pro 实际不可用（所有组合报错），不要尝试
- **永远不用外部 TTS**（gTTS/Edge-TTS/macOS say），所有音频一律从 Seedance 视频中提取

## 实战踩坑（已验证）

### 1.5 Pro 专项
- **分辨率默认 1080p**，不要用 720p（画面模糊）
- **首尾帧图片上传限制（2026-04-27 实测）**：
  - 服务端对 base64 内嵌 payload 有大小限制（非官方文档，实测结论）
  - 单帧 PNG 3MB（base64 ~4MB）：成功
  - 双帧 PNG 3MB×2（base64 ~8MB）：超时（`The write operation timed out`）
  - 双帧 JPEG q=98（base64 ~2.25MB）：成功，肉眼无损
  - **规则：首尾帧模式传两张图时，用 JPEG q=98（`subsampling=0`）转存后再传，避免 PNG base64 过大超时。单帧模式可直传 PNG**
  - 官方文档建议"大文件请勿使用 Base64 编码"，也支持传公网 URL（服务端自行下载），但本地文件没有公网 URL 时用 q=98 JPEG 是最简方案
  - 原始 timeout 60s 已改为 300s（`_call_api` 函数），但单独改 timeout 不能解决双帧 PNG 问题
- **面膜上脸**：描述敷面膜过程 AI 必崩（边缘溶解/五官变形）→ 只描述手拿面膜包装，不描述上脸动作
- **印尼语语速**：12s 舒适区 30-35 词（2.5-2.9词/秒），原始脚本自然语速 ~2.6词/秒，不要自作主张精简
- **动作幅度**：英文堆 "NOT/FROZEN/5 degrees" 无效 → 用中文自然描述"轻轻摇了两下头，幅度很小"。2次英文失败就切中文
- **ffmpeg 拼接**：Seedance 原生 44100Hz，不要用 `-c copy` concat → 每段必须统一重编码 `-ar 48000 -r 24 -c:v libx264 -c:a aac`

### 2.0 专项
- **分辨率最高 720p**（不支持 1080p），1.5 Pro 最高 1080p
- **camera_fixed** 在 r2v（多模态参考）模式不支持
- 提示词含 "穆斯林/hijab" → 触发安全策略 → 用中性词（"得体长袖连衣裙""头巾/headscarf"）
- **r2v 多模态调用**：content 数组传 `{"type":"image_url","image_url":{"url":"asset://..."},"role":"reference_image"}` + `{"type":"video_url","video_url":{"url":"asset://..."},"role":"reference_video"}`
- **asset 素材是视频时**必须用 `video_url` + `reference_video`（不是 `image_url`），否则报 "the specified asset is not an image"
- **真人素材入库**只有控制台 GUI（控制台→开通管理→ComputerVision），没有 API

### 音频规则
- **所有视频音频一律从 Seedance 生成的视频中提取**，不使用任何外部 TTS
- S2 实拍素材段：也用首尾帧模式生成视频→提取音轨→贴到实拍画面上，保持全片音色一致
- 实拍素材第一步永远 `ffmpeg -an` 去音频
- 素材不足目标时长用 `tpad=stop_mode=clone` 补帧，不用 `-shortest`

## 提示词技巧（官方推荐）

公式：**主体 + 动作 + 环境 + 镜头运动 + 画风 + 声音**

```
写实风格，在温暖的室内自然光下，一个20岁印尼女生坐在镜头前，
快节奏地说："Habis maskeran muka gatal, jerawatan — itu maskernya yang bermasalah!"
表情从愤怒转为共情，手势自然，TikTok自拍角度，固定机位。
```
