# Video Clip Assembler — 技术架构文档

> 版本：1.0 | 更新日期：2026-04-01

---

## 1. 系统架构

```
浏览器 (localhost:8765)              Python 后端 (http.server)
┌─────────────────────┐            ┌──────────────────────────┐
│  index.html          │            │  server.py (521行)        │
│  app.js (692行)      │───HTTP───→│    ├─ transcriber.py      │
│  style.css (652行)   │            │    ├─ translator.py       │
│  SortableJS (CDN)    │            │    ├─ video_processor.py  │
│                      │←──JSON────│    └─ ass_generator.py    │
└─────────────────────┘            └──────────────────────────┘
                                          │           │
                                     Gemini API    ffmpeg
                                    (转录/翻译)   (视频处理)
```

**架构选择理由**：
- 使用 Python `http.server`（标准库），零外部 Web 框架依赖
- 前端纯 HTML/CSS/JS，无构建步骤
- 长任务（转录/视频生成）用 `threading.Thread` 异步执行，前端轮询状态

---

## 2. 目录结构

```
~/.claude/skills/video-clip-assembler/
├── docs/
│   ├── PRD.md              # 产品需求文档
│   ├── TECHNICAL.md        # 技术架构文档（本文件）
│   ├── API.md              # 接口文档
│   └── DEPLOY.md           # 部署指南
├── fonts/
│   └── NotoSansCJKsc-Bold.otf  # 商用字体 (16MB, OFL许可)
├── scripts/
│   ├── server.py           # HTTP 后端主程序 (521行)
│   ├── transcriber.py      # Gemini 转录模块 (162行)
│   ├── translator.py       # Gemini 翻译+关键词匹配 (130行)
│   ├── video_processor.py  # ffmpeg 视频处理 (299行)
│   ├── ass_generator.py    # ASS 字幕生成器 (189行)
│   └── launch.sh           # 一键启动脚本 (44行)
├── static/
│   ├── index.html          # 前端页面 (188行)
│   ├── app.js              # 前端逻辑 (692行)
│   └── style.css           # 样式 (652行)
└── temp/                   # 运行时目录（自动创建）
    ├── clips/              # 上传的原始视频
    └── build_xxxx/         # 构建中间产物
```

**总代码量**：约 2,900 行（Python 1,301 + JS 692 + HTML 188 + CSS 652 + Shell 44）

---

## 3. 模块详解

### 3.1 server.py — HTTP 服务器

**职责**：路由分发、静态文件服务、全局状态管理、异步任务调度

**全局状态**：
```python
state = {
    "clips": {},              # clip_id → {path, filename, sentences}
    "task_status": "idle",    # idle/transcribing/building/subtitle_choice/done/error
    "task_progress": 0,       # 0-100
    "task_message": "",       # 状态文字
    "task_stage": "",         # trimming/concat/subtitle/burning/compressing
    "output_path": None,      # 成品视频路径
    "vocabulary": [],         # 用户输入的专有名词
    "language": "id",         # 音频语言
    "build_data": None,       # Phase 1 结果（供 Phase 2 使用）
}
```

**异步模式**：
- 转录和视频构建都在 `threading.Thread(daemon=True)` 中运行
- 前端通过 `GET /api/status` 每秒轮询进度
- 通过 `progress_callback` 回调函数更新 state

**文件上传**：
- 采用流式上传（非 multipart），通过 `X-Filename` header 传文件名
- 按 64KB 分块读取 body，写入 `temp/clips/` 目录

### 3.2 transcriber.py — 音频转录

**流程**：
```
视频文件
  → ffmpeg 提取音频 (MP3, 16kHz, mono, 64kbps)
  → genai.upload_file() 上传到 Gemini File API
  → 等待 PROCESSING → ACTIVE
  → Gemini 2.5 Flash 生成带时间戳的 JSON
  → 解析、清理、返回句子列表
```

**Gemini 提示词策略**：
- 按句号/问号/感叹号逐句拆分，优先 1-5 秒短句
- 语言特定提示（保留口语词、助词等）
- 支持专有名词注入（vocabulary hint）

**返回格式**：
```json
[
  {"text": "wow beneran ya", "start": 2.05, "end": 5.10, "words": []},
  {"text": "jadi gini ceritanya", "start": 5.30, "end": 8.20, "words": []}
]
```

### 3.3 translator.py — 翻译与关键词

**翻译**：
- 批量翻译（一次调用传所有句子）
- 支持任意源语言 → 中文
- 返回原句子列表，附加 `translation` 字段

**关键词匹配**：
- 输入：中文关键词列表 + 原文句子
- Gemini 在原文中查找对应词（只从实际转录文本中选词）
- 输出：`{"真的": "beneran", "百万": "juta"}`

**关键词分类**：
- 6 个内置分类：数字、金额、时间、年龄、品牌名、强调词
- Gemini 自动从转录文本中识别并归类

### 3.4 video_processor.py — 视频处理

**两阶段构建**：

```
Phase 1: build_video_phase1()
  ├── merge_consecutive_segments()  # 合并连续句子
  ├── trim_segment() × N            # ffmpeg 逐段裁剪
  ├── concat_segments()              # ffmpeg concat 拼接
  └── 返回 {concat_path, subtitle_segments}

  ──── 暂停，等用户选择是否加字幕 ────

Phase 2a: build_video_phase2_subtitle()
  ├── generate_ass()                 # 生成 ASS 字幕文件
  ├── burn_subtitles()               # ffmpeg 烧录字幕
  └── _compress_if_needed()          # 超 200MB 自动压缩

Phase 2b: build_video_phase2_no_subtitle()
  └── _compress_if_needed()          # 直接输出/压缩
```

**关键 ffmpeg 参数**：
| 操作 | 命令要点 |
|------|----------|
| 裁剪 | `-ss` 在 `-i` 后（帧精确），padding ±0.1s |
| 编码 | `-c:v libx264 -preset fast -crf 18` |
| 音频 | `-c:a aac -b:a 128k -ar 44100 -ac 2` |
| 拼接 | concat demuxer，先 normalize 再 copy |
| 字幕 | `-vf "ass=path:fontsdir=path"` |
| 压缩 | scale 到 max 1920px，CRF 23 |

**片段合并算法**：
```
遍历用户选择的句子序列：
  如果当前句子与上一句来自同一视频 && 时间间隔 < 1.0s：
    → 合并到同一组（扩展 end 时间）
  否则：
    → 创建新组
效果：原本需要 10 次 trim 的可能合并为 3 次
```

### 3.5 ass_generator.py — 字幕生成

**ASS 格式要点**：
```
PlayResX: 1080, PlayResY: 1920  (竖屏)
Font: Noto Sans CJK SC, 55pt, Bold
Alignment: 2 (底部居中)
Outline: 3.5, Shadow: 1.5
MarginV: 130 (距底部)
```

**关键词高亮实现**：
```
普通文字: wow ya ini
关键词:   wow {\fs138\1c&H00FFFF&}beneran{\r} ya
```

**智能分行**：
- 最多 6 词/行
- 优先在印尼语连词（dan/tapi/karena/yang/kalau 等 34 个词）后断行
- 优先在逗号后断行
- 避免最后一行只剩 1 个词

---

## 4. 依赖清单

| 组件 | 版本 | 来源 | 用途 |
|------|------|------|------|
| Python | 3.9+ | 系统 | 运行环境 |
| google-generativeai | 0.8.6 | xhs venv | Gemini API（转录/翻译/关键词） |
| imageio-ffmpeg | 0.6.0 | xhs venv | ffmpeg 二进制路径 |
| httpx | 0.28.1 | xhs venv | HTTP 客户端（备用） |
| http.server | stdlib | Python | Web 服务器 |
| threading | stdlib | Python | 异步任务 |
| SortableJS | 1.15.0 | CDN | 前端拖拽排序 |
| Noto Sans CJK SC | Bold | 本地 fonts/ | 字幕字体（OFL 许可） |

**Python venv 路径**：`~/.claude/skills/xhs-video-downloader/.venv`

---

## 5. 前端架构

### 状态管理
纯 JS 全局变量，无框架：
```javascript
currentStep        // 当前步骤 (1-6)
uploadedFiles      // [{id, filename}, ...]
clipsData          // 转录结果
selectedSentences  // 已勾选的句子
sortedGroups       // 排序后的分组
keywordMap         // 关键词映射
autoKeywordMap     // 自动检测的关键词
```

### 通信模式
- 所有请求用 `fetch()` API
- 文件上传：raw body + `X-Filename` header（非 multipart）
- 长任务：POST 触发 → 每秒 GET 轮询 status
- JSON 交互：`Content-Type: application/json`

### 拖拽排序
- SortableJS 两层嵌套：外层组排序 + 内层句子排序
- 句子可跨组拖拽（`group: 'sentences'`）
- 拖拽结束后通过 `onEnd` 回调同步 JS 状态

---

## 6. 已知限制

| 限制 | 原因 | 规避方案 |
|------|------|----------|
| 单用户 | http.server 单线程 | v2 迁移到 FastAPI/Flask |
| Gemini 25MB 音频限制 | API 限制 | 长视频需提前剪短 |
| 无持久化存储 | 重启丢失所有状态 | v2 加数据库 |
| 字幕仅支持竖屏 1080×1920 | ASS PlayRes 硬编码 | v2 自动检测视频分辨率 |
| 无用户认证 | 本地使用设计 | 部署时需加 auth |
