# Video Clip Assembler — API 接口文档

> 版本：1.0 | 基础地址：`http://localhost:8765`

---

## 概览

| 方法 | 路径 | 功能 | 耗时 |
|------|------|------|------|
| GET | `/` | 主页面 | 即时 |
| GET | `/api/status` | 查询任务状态 | 即时 |
| GET | `/api/clips` | 获取所有片段数据 | 即时 |
| GET | `/api/download` | 下载成品视频 | 即时 |
| POST | `/api/upload` | 上传视频文件 | 取决于文件大小 |
| POST | `/api/clear` | 清空所有片段 | 即时 |
| POST | `/api/vocabulary` | 设置专有名词和语言 | 即时 |
| POST | `/api/transcribe` | 启动转录+翻译 | 异步，30s-5min |
| POST | `/api/keywords` | 中文关键词→原文匹配 | 3-10s |
| POST | `/api/keyword-categories` | 自动分类关键词 | 3-10s |
| POST | `/api/build` | Phase 1：裁剪+拼接 | 异步，10s-2min |
| POST | `/api/continue-build` | Phase 2：字幕/输出 | 异步，10s-3min |

---

## 接口详情

### GET /api/status

查询当前异步任务的进度。前端每秒轮询一次。

**响应**：
```json
{
  "status": "transcribing",
  "progress": 45,
  "message": "转录中 (2/5)...",
  "stage": ""
}
```

**status 取值**：

| 值 | 含义 |
|----|------|
| `idle` | 空闲 |
| `transcribing` | 正在转录 |
| `translating` | 正在翻译 |
| `building` | 正在构建视频 |
| `subtitle_choice` | Phase 1 完成，等待用户选择是否加字幕 |
| `done` | 任务完成 |
| `error` | 任务出错 |

**stage 取值**（仅 building 状态）：`trimming` / `concat` / `subtitle` / `burning` / `compressing`

---

### POST /api/upload

流式上传单个视频文件。

**请求头**：
```
Content-Type: application/octet-stream
X-Filename: interview_01.mp4
```

**请求体**：文件二进制内容（raw body）

**响应**：
```json
{
  "id": "a1b2c3d4",
  "filename": "interview_01.mp4"
}
```

**说明**：
- 每次调用上传一个文件，多文件需多次调用
- 文件保存到 `temp/clips/` 目录
- 返回的 `id` 用于后续引用该片段

---

### POST /api/clear

清空所有已上传的片段和转录数据。

**请求体**：无

**响应**：
```json
{"status": "cleared"}
```

---

### POST /api/vocabulary

设置专有名词列表和音频语言。应在转录前调用。

**请求体**：
```json
{
  "vocabulary": ["Veirfoo", "PDRN", "Tulandut"],
  "language": "id"
}
```

**language 支持值**：`id` / `ko` / `ja` / `zh` / `auto`

**响应**：
```json
{"status": "ok"}
```

---

### POST /api/transcribe

启动异步转录+翻译任务。通过 `/api/status` 轮询进度。

**请求体**：无

**处理流程**：
1. 遍历所有已上传片段
2. 每段：提取音频 → Gemini 转录 → 更新进度
3. 全部转录完成后批量翻译
4. 状态变为 `done`

**响应**：
```json
{"status": "started"}
```

**轮询示例**：
```javascript
const poll = setInterval(async () => {
  const res = await fetch('/api/status');
  const data = await res.json();
  if (data.status === 'done') {
    clearInterval(poll);
    // 加载转录结果
  }
}, 1000);
```

---

### GET /api/clips

获取所有片段及其转录结果。

**响应**：
```json
{
  "clips": {
    "a1b2c3d4": {
      "filename": "interview_01.mp4",
      "sentences": [
        {
          "text": "wow beneran ya",
          "start": 2.05,
          "end": 5.10,
          "translation": "哇真的吗",
          "words": []
        }
      ]
    }
  }
}
```

---

### POST /api/keywords

将中文关键词匹配到原文对应词。

**请求体**：
```json
{
  "keywords": ["真的", "百万", "一天"]
}
```

**响应**：
```json
{
  "matches": {
    "真的": "beneran",
    "百万": "juta",
    "一天": "sehari"
  }
}
```

---

### POST /api/keyword-categories

按分类自动检测关键词。

**请求体**：
```json
{
  "categories": ["numbers", "money", "brand"]
}
```

**支持分类**：`numbers` / `money` / `time` / `age` / `brand` / `emotion`

**响应**：
```json
{
  "keywords": {
    "500 ribu": "money",
    "sehari": "time",
    "Veirfoo": "brand"
  }
}
```

---

### POST /api/build

启动 Phase 1：裁剪已选句子对应的视频片段并拼接。

**请求体**：
```json
{
  "selections": [
    {
      "clip_id": "a1b2c3d4",
      "sentence_idx": 0,
      "text": "wow beneran ya",
      "start": 2.05,
      "end": 5.10,
      "words": []
    }
  ],
  "keyword_highlights": {
    "beneran": true,
    "juta": true
  }
}
```

**响应**：
```json
{"status": "building"}
```

**后续**：
- 轮询 `/api/status`，当 `status === "subtitle_choice"` 时说明 Phase 1 完成
- 此时前端显示「加字幕」/「直接下载」按钮

---

### POST /api/continue-build

Phase 2：根据用户选择，烧录字幕或直接输出。

**请求体**：
```json
{
  "burn_subtitle": true
}
```

| burn_subtitle | 行为 |
|--------------|------|
| `true` | 生成 ASS 字幕 → 烧录到视频 → 压缩（如需要） |
| `false` | 跳过字幕 → 直接压缩输出（如需要） |

**响应**：
```json
{"status": "building"}
```

**后续**：轮询 `/api/status`，`status === "done"` 时调用下载接口。

---

### GET /api/download

下载成品视频文件。

**响应**：`application/octet-stream`，文件名 `output.mp4`

**前提**：`/api/status` 返回 `status: "done"`

---

## CORS

所有响应包含：
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, X-Filename
```
