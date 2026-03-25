---
type: prompt
product: "VEIRFOO PDRN人皮面膜"
template: "02 认知科普型（韩国成分科普）"
model: "Kirana"
platform: "Veo"
status: "已生成，S1已验证v3通过"
tags: [提示词, Kirana, 02, 认知科普, Veo, PDRN]
date: 2026-03-25
---

# 02「韩国皮肤科最火的成分」Veo 逐段提示词 — S1-S4

## 视频概述

**叙事逻辑**：韩国 PDRN 钩子 → 产品手持介绍 → 数据背书上脸 → CTA

**核心卖点织入**：
- S1：PDRN 排队三个月 / 打一针几百万 → 稀缺锚点
- S2：手持银管，成分同源韩国诊所 → 可信度
- S3：14天黄度-31%，第三方人体临床 → ⚠️ 数据类台词，易触发旁白
- S4：CTA，一管=一次 treatment → 转化

---

## 分镜脚本全表

| # | 时长/分辨率 | 首帧 | 尾帧 | 台词（印尼语） | 中文 | 动作 |
|---|-----------|------|------|--------------|------|------|
| S1 | 8s/720p | `02_S1_first.jpg` | `02_S1_last.jpg` | *"Bahan paling laris di klinik kulit Korea? PDRN. Antriannya tiga bulan, sekali suntik jutaan. Tapi sekarang nggak perlu ke Korea."* | 韩国皮肤科最火成分？PDRN。排队三个月，打一针几百万。但现在不用去韩国了。 | 直视镜头，坐姿从容有胸有成竹感 |
| S2 | 8s/720p | `02_S2_first.jpg` | `02_S2_last.jpg` | *"VEIRFOO Salmon Mask — PDRN dari DNA salmon, persis sumbernya sama dengan klinik Korea. Plus 500D micro-collagen dan 8D hyaluronic acid. Satu tube ada semua."* | VEIRFOO 人皮面膜——三文鱼 DNA 的 PDRN，和韩国诊所同源。加 500D 微胶原 + 8D 玻尿酸，一管全都有。 | 手持银管举起，从容自信 |
| S3 | 8s/720p | `02_S3_first.jpg` | `02_S3_last.jpg` | *"Empat belas hari warna kuning berkurang tiga puluh satu persen — ini bukan klaim iklan, ini hasil uji klinis manusia pihak ketiga."* | 14天肤色黄度降低31%——这不是广告说法，是第三方人体临床测试结果。 | 轻触脸颊，微微前倾，满足神情 |
| S4 | 8s/720p | `02_S4_first.jpg` | `02_S4_last.jpg` | *"Satu tube bahannya setara satu treatment klinik Korea. Made in Korea, BPOM certified. Komen 'PDRN' aku kirim info produknya."* | 一管成分等于一次韩国诊所 treatment。韩国制造，BPOM认证。评论 'PDRN' 我发产品信息。 | 手持银管，从容自信看镜头，CTA |

---

## 固定 Negative Prompt

```
voiceover, narration, documentary style, announcement voice, off-screen narrator,
statistics reading, exaggerated expressions, dramatic gestures, theatrical performance,
text overlay, subtitle, caption, camera zoom, camera push, background music,
dark skin, yellow skin, warm color cast, foggy, hazy, soft focus, washed out, blurry
```

> ⚠️ `statistics reading` 是防止 S3 数据类台词触发旁白的关键词，不能删

---

## S1 | 8s / 720p | 开场钩子·直视镜头

**首帧**：`02_S1_first.jpg` | **尾帧**：`02_S1_last.jpg` | **验证状态**：✅ v3 已通过 (2.0 MB)

```
Woman on cream ivory sofa by a window with sheer curtains, soft natural side light,
bright airy cream interior, soft bokeh background.
She sits with quiet knowing posture, one hand resting gently on her knee,
looking directly at camera with subtle knowing expression,
speaks naturally and conversationally as if telling a close friend:
'Bahan paling laris di klinik kulit Korea? PDRN.
Antriannya tiga bulan, sekali suntik jutaan. Tapi sekarang nggak perlu ke Korea.'
Calm serene wealthy young woman, subtle refined expressions, gentle composed demeanor.
Minimal natural gestures, NOT exaggerated. Fixed camera, no movement.
Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands,
no extra limbs, no extra fingers, no deformed hands, no floating limbs.
```

---

## S2 | 8s / 720p | 手持银管·成分介绍

**首帧**：`02_S2_first.jpg` | **尾帧**：`02_S2_last.jpg` | **验证状态**：✅ 已通过

```
Woman on cream ivory sofa by a window with sheer curtains, soft natural side light,
bright airy cream interior, soft bokeh background.
She holds up a silver cylindrical tube at chest height, calm confident expression,
looking at camera,
speaks naturally and conversationally as if telling a close friend:
'VEIRFOO Salmon Mask — PDRN dari DNA salmon,
persis sumbernya sama dengan klinik Korea.
Plus 500D micro-collagen dan 8D hyaluronic acid. Satu tube ada semua.'
Calm serene wealthy young woman, subtle refined expressions, gentle composed demeanor.
Minimal natural gestures, NOT exaggerated. Fixed camera, no movement.
Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands,
no extra limbs, no extra fingers, no deformed hands, no floating limbs.
Show ONLY the silver cylindrical tube — ignore any box or cardboard packaging.
```

---

## S3 | 8s / 720p | 上脸展示·数据背书

**首帧**：`02_S3_first.jpg` | **尾帧**：`02_S3_last.jpg` | **验证状态**：✅ v2 已通过

> ⚠️ **数据类台词注意**：台词含数字（tiga puluh satu persen = 31%），天然触发旁白模式。
> 已用「as if telling a close friend」包裹 + negative prompt 加 `statistics reading`。
> 数字用印尼语拼写（tiga puluh satu persen 而非 31%）。

```
Woman on cream ivory sofa by a window with sheer curtains, soft natural side light,
bright airy cream interior, soft bokeh background.
She gently touches her cheek with fingertips, slight forward lean, composed satisfied expression,
speaks naturally and conversationally as if telling a close friend, direct eye contact:
'Empat belas hari warna kuning berkurang tiga puluh satu persen —
ini bukan klaim iklan, ini hasil uji klinis manusia pihak ketiga.'
Calm serene wealthy young woman, subtle refined expressions, gentle composed demeanor.
Minimal natural gestures, NOT exaggerated. Fixed camera, no movement.
Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands,
no extra limbs, no extra fingers, no deformed hands, no floating limbs.
```

---

## S4 | 8s / 720p | CTA·手持产品

**首帧**：`02_S4_first.jpg` | **尾帧**：`02_S4_last.jpg` | **验证状态**：✅ 已通过

```
Woman on cream ivory sofa by a window with sheer curtains, soft natural side light,
bright airy cream interior, soft bokeh background.
She holds up a silver cylindrical tube at chest height,
looking at camera with composed confident expression,
speaks naturally and conversationally as if telling a close friend:
'Satu tube bahannya setara satu treatment klinik Korea.
Made in Korea, BPOM certified.
Komen PDRN aku kirim info produknya.'
Calm serene wealthy young woman, subtle refined expressions, gentle composed demeanor.
Minimal natural gestures, NOT exaggerated. Fixed camera, no movement.
Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands,
no extra limbs, no extra fingers, no deformed hands, no floating limbs.
Show ONLY the silver cylindrical tube — ignore any box or cardboard packaging.
```

---

## 参数备忘

| 段落 | 时长 | 分辨率 | 首帧路径 | 尾帧路径 |
|------|------|--------|---------|---------|
| S1 | 8s | 720p | `~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S1_first.jpg` | `…/02_S1_last.jpg` |
| S2 | 8s | 720p | `~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S2_first.jpg` | `…/02_S2_last.jpg` |
| S3 | 8s | 720p | `~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S3_first.jpg` | `…/02_S3_last.jpg` |
| S4 | 8s | 720p | `~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S4_first.jpg` | `…/02_S4_last.jpg` |

**产品图参考**：`~/Desktop/Veirfoo/微信图片_20260223160455_35_64.jpg`
**三视图**：`~/Desktop/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg`

---

## 视频输出路径

`~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S[编号]_v[版本].mp4`

## 关联笔记

- [[Kirana]] — 模特档案
- [[VEIRFOO PDRN人皮面膜]] — 产品资料
- 模板代码：`~/.claude/skills/kirana-video-workflow/templates/scene_prompts.py`（场景 key：`02_S1` ~ `02_S4`）

---

## 首尾帧生成命令（Nano Banana）

> 生成顺序：先跑所有首帧 → 确认 S1 背景最佳 → 用 S1 首帧作为 S2/S3/S4 的背景锚。
> ⚠️ S2/S4 持产品，产品图替换背景锚的第 3 个 `-r` 位置；可同时传 4 个 `-r`（脚本支持最多14张）

**通用路径**
- 三视图：`~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg`
- 产品图：`~/Desktop/Veirfoo/微信图片_20260223160455_35_64.jpg`
- 输出目录：`~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/`

---

### S1 首帧

```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py \
  "Woman on cream ivory sofa by a window with sheer white curtains, soft cool neutral daylight from the window on the left, bright airy cream interior, soft bokeh background. She sits with quiet knowing posture, one hand resting gently on her knee, looking directly at camera with subtle knowing expression. Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands, no floating limbs." \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -m "gemini-3-pro-image-preview" -a "9:16" -s "4K" \
  -n "02_S1_first" -o "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN"
```

### S1 尾帧

```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py \
  "Woman on cream ivory sofa by a window with sheer white curtains, soft cool neutral daylight from the window on the left, bright airy cream interior, soft bokeh background. She sits with calm composed posture looking at camera, one hand resting on knee, slight natural forward lean completing a composed knowing moment. Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands, no floating limbs." \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S1_first.jpg" \
  -m "gemini-3-pro-image-preview" -a "9:16" -s "4K" \
  -n "02_S1_last" -o "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN"
```

---

### S2 首帧（持产品）

```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py \
  "Woman on cream ivory sofa by a window with sheer white curtains, soft cool neutral daylight from the window on the left, bright airy cream interior, soft bokeh background. She holds up a slim smooth metallic silver cylindrical tube at chest height, looking at camera with calm confident expression. Show ONLY the silver cylindrical tube — ignore any box or cardboard packaging. Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands, no floating limbs." \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S1_first.jpg" \
  -r "~/Desktop/Veirfoo/微信图片_20260223160455_35_64.jpg" \
  -m "gemini-3-pro-image-preview" -a "9:16" -s "4K" \
  -n "02_S2_first" -o "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN"
```

### S2 尾帧（持产品）

```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py \
  "Woman on cream ivory sofa by a window with sheer white curtains, soft cool neutral daylight from the window on the left, bright airy cream interior, soft bokeh background. She holds a slim smooth metallic silver cylindrical tube at chest height, slightly adjusting her grip, looking at camera with composed confident expression. Show ONLY the silver cylindrical tube — ignore any box or cardboard packaging. Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands, no floating limbs." \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S2_first.jpg" \
  -r "~/Desktop/Veirfoo/微信图片_20260223160455_35_64.jpg" \
  -m "gemini-3-pro-image-preview" -a "9:16" -s "4K" \
  -n "02_S2_last" -o "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN"
```

---

### S3 首帧

```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py \
  "Woman on cream ivory sofa by a window with sheer white curtains, soft cool neutral daylight from the window on the left, bright airy cream interior, soft bokeh background. She gently touches her cheek with fingertips, slight forward lean, composed satisfied expression looking toward camera. Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands, no floating limbs." \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S1_first.jpg" \
  -m "gemini-3-pro-image-preview" -a "9:16" -s "4K" \
  -n "02_S3_first" -o "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN"
```

### S3 尾帧

```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py \
  "Woman on cream ivory sofa by a window with sheer white curtains, soft cool neutral daylight from the window on the left, bright airy cream interior, soft bokeh background. She gently lowers her hand from her cheek, looking at camera with a quietly satisfied composed expression, hand returning naturally to her lap. Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands, no floating limbs." \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S3_first.jpg" \
  -m "gemini-3-pro-image-preview" -a "9:16" -s "4K" \
  -n "02_S3_last" -o "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN"
```

---

### S4 首帧（持产品·CTA）

```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py \
  "Woman on cream ivory sofa by a window with sheer white curtains, soft cool neutral daylight from the window on the left, bright airy cream interior, soft bokeh background. She holds up a slim smooth metallic silver cylindrical tube at chest height, looking at camera with composed confident expression, ready to speak. Show ONLY the silver cylindrical tube — ignore any box or cardboard packaging. Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands, no floating limbs." \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S1_first.jpg" \
  -r "~/Desktop/Veirfoo/微信图片_20260223160455_35_64.jpg" \
  -m "gemini-3-pro-image-preview" -a "9:16" -s "4K" \
  -n "02_S4_first" -o "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN"
```

### S4 尾帧（持产品·CTA）

```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py \
  "Woman on cream ivory sofa by a window with sheer white curtains, soft cool neutral daylight from the window on the left, bright airy cream interior, soft bokeh background. She holds a slim smooth metallic silver cylindrical tube at chest height, looking at camera with a gentle natural smile and composed confident expression — warm and inviting close. Show ONLY the silver cylindrical tube — ignore any box or cardboard packaging. Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands, no floating limbs." \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/model/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg" \
  -r "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN/02_S4_first.jpg" \
  -r "~/Desktop/Veirfoo/微信图片_20260223160455_35_64.jpg" \
  -m "gemini-3-pro-image-preview" -a "9:16" -s "4K" \
  -n "02_S4_last" -o "~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN"
```
