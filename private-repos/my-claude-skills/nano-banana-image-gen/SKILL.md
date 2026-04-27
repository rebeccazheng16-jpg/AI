# Nano Banana Pro 图片生成器

通过 Gemini API (`gemini-3-pro-image-preview`) 直接生成图片。用户只需用自然语言（中文或英文）描述想要的画面，本 skill 自动完成：提示词优化 → API 调用 → 图片下载保存。

## 触发方式

当用户出现以下任一意图时，使用此 skill：
- "帮我生成一张图片"、"生成图"、"出图"、"画一张"
- "帮我生成xxx的图"
- "用 Gemini / Nano Banana 生成"
- "调 API 生成图片"
- 给出了提示词并希望直接生成图片
- 在迭代编辑中说"再调整一下"、"改一下"、"重新生成"
- 提供了参考图片并要求生成/合成新图

## 核心脚本

```
~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py
```

### 调用方式

**纯文本生成（使用所有默认参数）：**
```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py "英文提示词" -n "文件名" -o "输出目录"
```

**指定宽高比（覆盖auto）：**
```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py "英文提示词" -a "9:16" -n "文件名"
```

**带参考图合成（产品植入/风格参考等）：**
```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py "英文提示词" -r "图片1路径" -r "图片2路径" -n "文件名"
```

### 参数说明
| 参数 | 说明 | 默认值 |
|------|------|--------|
| prompt (必填) | 英文提示词 | - |
| -n / --name | 输出文件名（不含扩展名） | gemini_时间戳 |
| -o / --output-dir | 输出目录 | ~/Desktop |
| -r / --ref | 参考图片路径（可多次使用，最多14张） | 无 |
| -m / --model | 模型名称 | **gemini-3-pro-image-preview** |
| -t / --temperature | 温度参数 | **1.0** |
| -a / --aspect-ratio | 宽高比 | **auto**（不传参，模型自动决定） |
| -s / --image-size | 分辨率 | **4K** |

### 默认行为（自动应用，无需每次指定）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| **模型** | `gemini-3-pro-image-preview` | Nano Banana Pro，支持 4K 和精准文字渲染 |
| **Temperature** | `1.0` | Google 官方推荐值，低于 1.0 可能导致输出循环 |
| **分辨率** | `4K` | 4096x4096，仅 gemini-3-pro 支持 |

> **视频项目出图规则**：当图片最终用途是 Seedance/Veo 视频首尾帧时，使用 `-s 1K`（1080p）直接出图，避免生成 4K 再压缩产生大量中间文件。4K 仅用于需要高清印刷或独立展示的图片。
| **宽高比** | auto | 不指定 aspectRatio，模型自动决定；有参考图时匹配输入图尺寸 |

> **关于宽高比 auto**：Google API 不支持 `"auto"` 字符串值。实现方式是**不传 aspectRatio 参数**，让模型自动选择最佳比例。如果用户明确要求特定比例（如 9:16），通过 `-a` 参数覆盖。

### 可选模型对比

| 模型 | 速度 | 4K支持 | 适用场景 |
|------|------|--------|----------|
| **gemini-3-pro-image-preview** (默认) | 较慢 | 支持 | 高质量出图、精准文字、产品图 |
| gemini-2.5-flash-image | 快 | 不支持 | 快速迭代、草稿预览 |
| gemini-2.0-flash-exp-image-generation | 快 | 不支持 | 旧版兼容 |

如需快速预览可用 `-m gemini-2.5-flash-image`。

## 完整工作流程

### 步骤 1：理解用户意图

分析用户的自然语言描述，判断属于哪种场景：
- **A. 纯文本生成**：用户描述一个画面，从零生成
- **B. 多图合成**：用户提供参考图 + 描述，合成新图（如产品植入）
- **C. 迭代编辑**：在已有生成结果上微调

### 步骤 2：转化为优化英文提示词

**必须遵循 nano-banana-prompt-optimizer skill 的所有规范**，核心要点：

1. **用自然语言描述场景，不要堆砌关键词**
2. **结构公式**：`[主体+形容词] 正在 [动作] 在 [场景/地点], [构图/镜头角度], [光线/氛围], [风格/媒介]`
3. **具体且描述性强**：明确材质、纹理、氛围、镜头参数
4. **不要在提示词中写 "Aspect ratio 9:16" 之类的文字**——宽高比通过 API 参数 `-a` 控制，不写在提示词里
5. 用英文书写最终提示词（Gemini 对英文效果更好）

### 步骤 3：向用户展示优化后的提示词

在调用 API **之前**，先展示：
```
【优化后提示词（英文）】
...

【中文参考】
...

【API 参数】
模型: gemini-3-pro-image-preview | 温度: 1.0 | 分辨率: 4K | 宽高比: auto
```

让用户确认或调整后再生成。**如果用户说"直接生成"或语气明确，可以跳过确认直接调用。**

### 步骤 4：调用 API 生成图片

使用 Bash 工具执行 Python 脚本：

**场景 A - 纯文本生成（auto 宽高比）：**
```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py "优化后的英文提示词" -n "描述性文件名" -o "输出目录"
```

**场景 A - 纯文本生成（指定宽高比）：**
```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py "优化后的英文提示词" -a "9:16" -n "文件名" -o "输出目录"
```

**场景 B - 多图合成（如产品植入）：**
```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py "合成提示词" -r "人物图路径" -r "产品图路径" -n "文件名" -o "输出目录"
```

**场景 C - 迭代编辑（基于已有生成图）：**
```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py "编辑指令" -r "上一次生成的图片路径" -n "文件名_v2" -o "输出目录"
```

**快速预览模式（用 2.5 Flash）：**
```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py "提示词" -m "gemini-2.5-flash-image" -n "preview" -o "输出目录"
```

### 步骤 5：展示结果

生成完成后向用户报告：
- 图片保存路径
- 文件大小
- 如果生成失败，分析原因并建议调整

## 输出格式

```
【用户意图】
简述用户想要什么

【优化后提示词（英文）】
完整的优化英文提示词

【中文参考】
提示词的中文翻译

【API 参数】
模型: gemini-3-pro-image-preview | 温度: 1.0 | 分辨率: 4K | 宽高比: auto/9:16

（调用 API 生成中...）

【生成结果】
- 保存路径：...
- 文件大小：...

【后续建议】
- 迭代微调建议1
- 迭代微调建议2
```

## 与其他 skill 的协作

| 场景 | 协作方式 |
|------|----------|
| 用户给了中文描述要生成图 | 本 skill 内部按 **nano-banana-prompt-optimizer** 规范转化为英文 |
| 用户要加产品到图中 | 按 **nano-banana-product-placement** 规范生成合成提示词，然后调用 API |
| 用户要反推图片提示词再生成 | 先用 prompt-optimizer 的流程B反推，再用本 skill 生成 |

## 迭代编辑最佳实践

Gemini 擅长对话式迭代编辑。当用户对已生成的图片说"调整一下"时：

1. **优先用迭代指令**，而非重新生成完整提示词
2. 将上一次生成的图片作为参考图（-r 参数）传入
3. 用简洁的编辑指令描述变更
4. 例如：`Make the smile more subtle` / `Move the product closer to her face` / `Make the lighting warmer`

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| HTTP 429 (限速) | 等待 30 秒后重试 |
| HTTP 400 (请求无效) | 检查提示词是否过长或包含违规内容 |
| 安全过滤 | 调整提示词，去除可能触发过滤的描述 |
| 超时 | 4K 生成较慢，超时已设为 300 秒；可用 `-s 1K` 降低分辨率加速 |
| 无图片返回 | 检查 responseModalities 是否正确 |
| imageSize 不支持 | 仅 gemini-3-pro-image-preview 支持 4K，其他模型自动忽略 |

## 实战踩坑（已验证）

- **imageSize 只接受预设值** `512/1K/2K/4K`，不接受像素尺寸（`1920x1080` → HTTP 400）。要 1080p：用 `2K` 生成（9:16 输出 1536×2752），PIL LANCZOS 下采样到 1080×1920
- **不要用 1K 再超分到 1080p**：超分无细节增益，是假高清。用户没说分辨率时默认 `-s 4K` 出真实 4K
- **不写 "selfie"**：会生成手机入镜。改用 `camera positioned slightly above eye level looking down` + `NOT holding a phone, no phone in frame`
- **"medium shot from waist up" 出全身**：模型理解比预期宽。口播构图用 `tight close-up, head and shoulders only, face fills the upper two-thirds of the frame`
- **暖光融合提示词全场景通用**：学会一个有效的光影融合写法后，桌面/手持/任何产品位置统一使用，不要场景换了就忘
- **出图后必须自审**：检查手指数/肢体数/产品变形/面部一致性，不通过静默重跑（最多2次），不给用户看废图
- **产品入帧先确认实物尺寸**：写进提示词，不能让 AI 自由发挥比例

## API 信息

- **API Key**：已内置于脚本中
- **模型**：gemini-3-pro-image-preview (Nano Banana Pro)
- **端点**：generativelanguage.googleapis.com/v1beta
- **超时**：300 秒（4K 生成需要更多时间）
- **支持的参考图格式**：PNG, JPG, JPEG, WebP, GIF
- **最多参考图数量**：14 张
- **支持的宽高比**：1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
- **支持的分辨率**：1K (1024), 2K (2048), 4K (4096) — 仅 gemini-3-pro
