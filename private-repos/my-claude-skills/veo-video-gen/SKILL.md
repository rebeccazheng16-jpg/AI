# Veo 3.1 视频生成器

通过 Gemini API (`veo-3.1-generate-preview`) 生成高质量视频。用户只需用自然语言描述想要的画面，本 skill 自动完成：提示词优化 → API 提交 → 轮询等待 → 视频下载保存。

## 触发方式

当用户出现以下任一意图时，使用此 skill：
- "帮我生成一段视频"、"生成视频"、"出视频"、"做一段视频"
- "用 Veo 生成"、"用 Gemini 生成视频"
- "帮我生成xxx的视频"
- 给出了视频描述并希望直接生成
- 在迭代中说"再生成一段"、"换个视频"

## 核心脚本

```
~/.claude/skills/veo-video-gen/scripts/veo_video_gen.py
```

### 调用方式

**基本用法：**
```bash
python3 ~/.claude/skills/veo-video-gen/scripts/veo_video_gen.py "英文视频描述" -n "文件名" -o "输出目录"
```

**图生视频（用图片作为起始帧）：**
```bash
python3 ~/.claude/skills/veo-video-gen/scripts/veo_video_gen.py "英文视频描述" -i "图片路径" -n "文件名" -o "输出目录"
```

**首尾帧插值（interpolation / first+last frame）：**
```bash
# 720p 支持 4/6/8 秒，首尾帧模式不限制必须 8 秒
python3 ~/.claude/skills/veo-video-gen/scripts/veo_video_gen.py "英文视频描述" \
  -i "首帧路径.png" -l "尾帧路径.png" \
  -r 720p -d 4 \
  -n "文件名" -o "输出目录"
```

**带负面提示词（强烈建议始终使用）：**
```bash
python3 ~/.claude/skills/veo-video-gen/scripts/veo_video_gen.py "英文视频描述" --negative-prompt "extra limbs, extra fingers, deformed hands, blurry" -n "文件名" -o "输出目录"
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| prompt (必填) | 英文视频描述 | - |
| -n / --name | 输出文件名（不含扩展名） | veo_时间戳 |
| -o / --output-dir | 输出目录 | ~/Desktop |
| -d / --duration | 视频时长（秒） | **8** |
| -a / --aspect-ratio | 宽高比 | **9:16** |
| -r / --resolution | 分辨率 | **4k** |
| -i / --image | 起始帧图片路径（图生视频 / 首尾帧模式首帧） | 无 |
| -l / --last-image | 尾帧图片路径（首尾帧模式，必须配合 -i 使用） | 无 |
| --negative-prompt | 负面提示词 | 无 |

### 默认行为

| 参数 | 默认值 | 说明 |
|------|--------|------|
| **宽高比** | `9:16` | 竖屏视频 |
| **分辨率** | `4k` | 最高画质 |
| **时长** | `8` 秒 | 4K 分辨率必须为 8 秒 |
| **数量** | `1` | 每次生成 1 个视频 |

### 时长与分辨率约束

| 分辨率 | 可选时长 |
|--------|----------|
| 720p | 4 / 6 / 8 秒 |
| 1080p | 仅 8 秒 |
| 4k | 仅 8 秒 |

---

## ⚠️ API 参数支持情况（官方文档，2026-03 更新）

| 参数/功能 | 支持情况 | 说明 |
|----------|---------|------|
| `referenceImages` | ✅ Veo 3.1 支持，最多 3 张 | 使用时 durationSeconds **必须为 "8"** |
| `personGeneration` | ✅ 支持 | 文生视频用 `"allow_all"`，图生视频用 `"allow_adult"` |
| `lastFrame` | ✅ 支持 | 必须配合 `image`（首帧）一起使用 |
| `video` | ✅ 支持（视频延伸） | 每次延伸 +7s，最多 20 次，仅支持 720p |
| `inlineData` 图片格式 | ❌ 不支持 | 用 `bytesBase64Encoded` + `mimeType` |
| `generateAudio` 参数 | ❌ 不支持 | Veo 3.1 自动生成音频，无法手动控制 |
| `numberOfVideos` 参数 | ❌ 不支持 | 每次只能生成 1 个 |
| 精确控制语音台词 | ❌ 不支持 | 只能描述语气和话题，不保证说出指定台词 |

### durationSeconds 必须为 "8" 的情况

以下情况必须传 `"8"`，否则 HTTP 400：
- 使用 `video` 参数（视频延伸）
- 使用 `referenceImages` 参数
- 分辨率为 `1080p` 或 `4k`

其他情况（纯文生/图生/首尾帧 + 720p）可以传 `"4"`、`"6"`、`"8"`。

---

## 🚨 提示词防畸形规则（核心，每次生成必须遵守）

### 规则 1：人体解剖学检查

**在写提示词之前，必须检查以下物理约束：**

- 人类只有 **2 只手、2 只脚、1 个头、5 根手指/脚趾**
- 如果一只手拿着物品，则只剩 1 只手可以做其他动作
- 如果需要双手做动作（如双手触摸脸部），必须先描述**放下物品**的过渡
- 不要在同一时刻描述矛盾的肢体动作

**反面示例（会导致三只手）：**
```
❌ She holds the product tube in her right hand while gently touching her face with both hands
```

**正确示例（分段描述）：**
```
✅ Segment 1 (0-3s): She holds the silver tube in her right hand, showing it to the camera.
   Segment 2 (3-4s): She places the tube down on the table.
   Segment 3 (4-8s): She gently touches both cheeks with her fingertips, smiling.
```

### 规则 2：必须使用负面提示词

**每次生成都必须加 `--negative-prompt`**，至少包含：
```
extra limbs, extra arms, extra hands, extra fingers, three hands, deformed body, mutated, unnatural anatomy, blurry, distorted
```

针对特定场景追加：
- 产品展示：`deformed tube, wrong text, melted product`
- 人物特写：`cross-eyed, deformed face, extra teeth`
- 手部特写：`six fingers, fused fingers, missing fingers`

### 规则 3：复杂动作必须分段

当视频涉及多个动作时，**必须将提示词按时间分段**：

```
Segment 1 (0-3s): [动作A的描述]
Segment 2 (3-5s): [过渡动作描述]
Segment 3 (5-8s): [动作B的描述]
```

这样可以避免 AI 同时渲染冲突动作。

### 规则 4：避免触发安全过滤器

以下描述可能触发 Veo 安全策略被拒绝：
- 过度详细的身体/衣着描述（如 "halter top revealing shoulders"）
- 明确指定某人说某种语言的具体台词
- 涉及医疗功效的直接声明

**安全写法：**
- 衣着用简洁词："casual outfit"、"stylish top" 代替详细描述
- 语音用暗示："speaks enthusiastically in Japanese about skincare" 代替逐字台词
- 功效用间接表述："showcasing the product's benefits" 代替医疗声明

### 规则 5：产品一致性

当用户提供产品图片时：
- 使用 `-i` 将图片作为起始帧，确保产品外观一致
- 在提示词中详细描述产品外观（颜色、材质、大小、文字）
- 避免让 AI 自由发挥产品设计

---

## 完整工作流程

### 步骤 1：理解用户意图

分析用户的自然语言描述，确定：
- 视频内容和场景
- 是否指定了时长（默认 8 秒）
- 是否有特殊分辨率或宽高比要求
- 是否提供了参考图片（→ 使用图生视频）

### 步骤 2：转化为优化英文提示词

**核心要点：**

1. **用自然语言描述场景和动作，不要堆砌关键词**
2. **视频提示词要包含动态元素**：人物动作、镜头运动、光影变化
3. **结构公式**：`[主体+外貌] 正在 [动作/运动] 在 [场景], [镜头运动], [光线/氛围变化], [风格]`
4. **描述时间流动**：如 "slowly turns to face the camera"
5. **复杂动作必须分段描述**（见规则 3）
6. **必须进行解剖学检查**（见规则 1）
7. **必须生成负面提示词**（见规则 2）
8. 用英文书写最终提示词

### 步骤 3：向用户展示优化后的提示词

在调用 API **之前**，先展示：
```
【优化后提示词（英文）】
...

【负面提示词】
...

【中文参考】
...

【视频参数】
时长: 8秒 | 比例: 9:16 | 分辨率: 4k
```

让用户确认或调整后再生成。**如果用户说"直接生成"或语气明确，可以跳过确认直接调用。**

### 步骤 4：调用 API 生成视频

使用 Bash 工具执行 Python 脚本：

```bash
source ~/.claude/skills/xhs-video-downloader/.venv/bin/activate && python3 ~/.claude/skills/veo-video-gen/scripts/veo_video_gen.py "提示词" --negative-prompt "负面提示词" -n "文件名" -o "输出目录"
```

**重要**：
- 必须先 `source` 激活 venv（依赖 imageio_ffmpeg）
- Bash 超时设置为 **600000 毫秒**（10 分钟）
- 多个视频可以用 `run_in_background` 并行生成

### 步骤 5：展示结果并自动打开

生成完成后：
- 报告保存路径、文件大小、生成耗时
- **自动用 `open` 命令打开视频文件**
- 如果生成失败，分析原因并建议调整

## 输出格式

```
【用户意图】
简述用户想要什么视频

【优化后提示词（英文）】
完整的优化英文视频描述

【负面提示词】
extra limbs, extra hands, ...（根据场景定制）

【中文参考】
提示词的中文翻译

【视频参数】
时长: 8秒 | 比例: 9:16 | 分辨率: 4k | 模式: 文生视频/图生视频

（调用 API 生成中，预计需要 2-5 分钟...）

【生成结果】
- 保存路径：...
- 文件大小：...
- 生成耗时：...
```

## 提示词质量检查清单

每次写完提示词后，**必须逐条检查**：

- [ ] **解剖学**：人物肢体数量是否正确？有没有矛盾动作？
- [ ] **时间分段**：复杂动作是否分段描述？有过渡吗？
- [ ] **负面提示词**：是否添加了防畸形的负面提示词？
- [ ] **安全过滤**：描述是否可能触发安全策略？需要委婉化？
- [ ] **产品一致性**：有参考图时是否用了 `-i` 起始帧？
- [ ] **物理合理性**：手拿着东西时另一只手的动作合理吗？物品大小比例对吗？

## 图生视频注意事项

- 图片格式：`bytesBase64Encoded` + `mimeType`（脚本已内置处理）
- 图片会作为视频第一帧，Veo 从这一帧开始生成动态内容
- 适合场景：产品图 → 手持展示、人物照 → 动态视频
- 提示词应描述"从这张图开始，接下来发生什么"

## 语音/配音限制

Veo 3.1 会自动生成配套音频，但**无法精确控制语音内容**：

| 能做到 | 做不到 |
|--------|--------|
| 描述说话的语气和情绪 | 指定逐字台词 |
| 暗示环境音效 | 精确控制音乐 |
| 指定大致语言（如 "speaks in Japanese"） | 保证说出特定句子 |

**如果需要精确台词**，建议方案：
1. 用 Veo 生成嘴巴在动的画面
2. 用 TTS（Edge-TTS/gTTS）生成精确语音
3. 用 ffmpeg 替换音轨

## 与其他 skill 的协作

| 场景 | 协作方式 |
|------|----------|
| 用户给了中文描述要生成视频 | 本 skill 内部转化为英文 |
| 用户先生成图片再要视频 | 用 `-i` 将图片作为起始帧 |
| 用户要求与图片风格一致 | 复用之前图片提示词的视觉元素，加入动态描述 |
| 需要精确配音 | 配合 TTS 工具生成语音后合并 |

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| HTTP 429 (限速) | 等待 60 秒后重试 |
| HTTP 400 "referenceImages isn't supported" | 改用 `-i`（起始帧）代替 `--ref` |
| HTTP 400 "inlineData isn't supported" | 脚本已修复，使用 bytesBase64Encoded |
| HTTP 400 (安全策略) | 检查提示词是否触发过滤器，委婉化描述 |
| HTTP 503 (服务繁忙) | 等待几分钟后重试 |
| 轮询超时 | 15 分钟未完成，建议稍后重试 |
| 生成结果畸形（多只手等） | 检查解剖学规则，添加负面提示词，分段描述动作 |

## API 信息

- **API Key**：已内置于脚本中
- **模型**：veo-3.1-generate-preview
- **端点**：generativelanguage.googleapis.com/v1beta
- **认证方式**：x-goog-api-key 请求头
- **生成模式**：异步（predictLongRunning → 轮询 → 下载）
- **轮询间隔**：15 秒
- **最大等待时间**：15 分钟（60 次轮询）
- **支持的宽高比**：9:16, 16:9
- **支持的分辨率**：720p, 1080p, 4k
- **支持的时长**：4, 6, 8 秒（4K/1080p 仅支持 8 秒）
- **图生视频**：支持（`-i` 参数，图片作为起始帧）
- **参考图片**：不支持（`referenceImages` 已被模型禁用）
