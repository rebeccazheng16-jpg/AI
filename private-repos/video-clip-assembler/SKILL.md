# Video Clip Assembler

AI驱动的采访视频自动剪辑系统。上传多段素材 → 自动转录翻译 → 网页勾选排序 → 一键输出带关键词高亮字幕的成品视频。

## 启动

```bash
bash ~/.claude/skills/video-clip-assembler/scripts/launch.sh
```

浏览器自动打开 `http://localhost:8765`。

## 依赖

全部来自 xhs venv（无需额外安装）：
- google-generativeai — Gemini 转录 + 翻译
- imageio-ffmpeg — ffmpeg 路径
- SortableJS 1.15 — CDN，前端拖拽

## 环境变量

| 变量 | 用途 |
|------|------|
| GEMINI_API_KEY | Gemini 转录 + 翻译 + 关键词匹配 |

## 工作流

1. **上传** — 拖放或选择多个视频文件（支持批量10+）
2. **转录** — Gemini 2.5 Flash 音频转录（印尼语，带时间戳）
3. **翻译** — Gemini 2.5 Flash 印尼语→中文
4. **勾选** — 在网页上选择需要的句子
5. **排序** — SortableJS 拖拽调整顺序
6. **关键词** — 输入中文关键词，Gemini 自动匹配印尼语原词
7. **生成** — ffmpeg 裁剪+拼接+ASS字幕烧录

## 字幕样式

- 普通词：白色 33px
- 关键词：黄色 66px（2倍放大）
- ASS格式，底部居中
- 裁剪点加 ±0.1s padding 防止截断语音

## 文件结构

```
scripts/
  server.py          # HTTP 后端
  transcriber.py     # Whisper API 转录
  translator.py      # Gemini 翻译 + 关键词匹配
  video_processor.py # ffmpeg 裁剪/拼接/烧字幕
  ass_generator.py   # ASS 字幕生成（关键词高亮）
  launch.sh          # 一键启动
static/
  index.html         # 单页应用
  app.js             # 前端逻辑
  style.css          # 暗色主题样式
temp/                # 运行时临时文件
```

## API

| Method | Path | 功能 |
|--------|------|------|
| GET | / | 页面 |
| POST | /api/upload | 上传视频 |
| POST | /api/transcribe | 转录+翻译 |
| GET | /api/status | 轮询进度 |
| GET | /api/clips | 获取全部转录结果 |
| POST | /api/keywords | 关键词匹配 |
| POST | /api/build | 生成视频 |
| GET | /api/download | 下载成品 |
