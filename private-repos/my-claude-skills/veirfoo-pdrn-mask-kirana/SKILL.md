# Kirana 首尾帧视频生成规范

> 基于 VEIRFOO PDRN 面膜 V1 认知科普型视频实战经验沉淀（2026-03）

## 角色信息

- **Soul**：看到你挖了一大勺鱼子酱直接送进嘴里并浮现痛苦的表情，她只会笑笑并说一句这东西真的好咸
- **定位**：印尼华裔穆斯林，luxury lifestyle 博主，心静如水，不表演
- **语言**：印尼语口播
- **三视图**：`~/Desktop/模特公式图/Kirana/Kirana_homewear_turnaround_v5.jpg`（唯一人脸锚点）

---

## 参考图规则

| 场景 | 传入参考图 | 说明 |
|------|-----------|------|
| 首帧（无产品） | 三视图 × 1 | 只传三视图，不加任何其他图 |
| 尾帧（延续首帧姿势） | 三视图 + 对应首帧 × 2 | 三视图锁人脸，首帧锁构图和光影 |
| 尾帧（有产品出现） | 三视图 + 持产品首帧 × 2 | 同上，确保产品外观一致 |

> ⚠️ **铁律：绝不把生成图链式传入下一帧**——每次漂移都会累积，三视图是唯一人脸来源

---

## Nano Banana 首尾帧提示词模板

### 光影描述（室内沙发场景 · 已验证）

```
soft natural light from a large window with sheer white curtains on the left side,
bright airy cream interior, soft bokeh background
```

> 这是与整个 V1 系列光影一致的描述，不要改成 studio light / even diffuse light（会显得平板或跳出）

### 提示词结构

```
[场景/家具/背景] + [光影描述] + [动作/姿势] + [构图] + [防畸形]
```

**关键规则：提示词里只写场景和动作，绝不写角色外观（头巾颜色、服装、肤色等）**
——外观完全由三视图参考图决定，文字描述会覆盖参考图

### 已验证的动作描述片段

| 场景类型 | 提示词片段 |
|---------|-----------|
| 思考/讲解 | `gently touches her cheek with one fingertip, slight thoughtful lean forward, looking toward camera with composed explaining expression` |
| 看手机→抬头 | `looking down at orange iPhone in hands, slight smile` → `gently lowers her iPhone and looks up at camera with composed knowing expression` |
| 讲解手势 | `one hand resting on knee, other hand slightly raised with subtle open-palm gesture — completing a clear point` |
| 持产品展示 | `holds up the silver foil mask sachet at chest height, looking at camera with composed confident expression` |
| CTA 指向 | `raises one finger toward camera with refined gesture, gentle composed smile` |

### 固定结尾防畸形词

```
Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands,
no extra limbs, no extra fingers, no deformed hands, no floating limbs.
```

### 生成参数

```bash
-r "~/Desktop/模特公式图/Kirana/Kirana_homewear_turnaround_v5.jpg"
-a "9:16" -s "4K" -m "gemini-3-pro-image-preview"
```

---

## Veo 视频提示词模板

### 结构公式

```
[场景/光影] + [人物状态] + [口播指令 + 台词] + [气质约束] + [镜头约束]
```

### 已验证的完整模板

```
Woman on cream ivory sofa by a window with sheer curtains, soft natural side light.
She [动作描述], speaks softly and unhurriedly in Indonesian with natural lip sync
throughout — gentle refined tone: '[台词]'.
Minimal natural gestures, subtle expressions, NOT exaggerated.
Fixed camera, no movement.
```

> ⚠️ Veo 提示词同样不写角色外观——由首帧图片决定

### 台词长度规则（8s 视频）

| 语速 | 词数 | 适用场景 |
|------|------|---------|
| 正常贵妇语速 | 18–21词 | 科普类、解释类 |
| 偏慢（留停顿感） | 14–17词 | CTA、情感类结尾 |
| 避免 | >22词 | 会出现口型提前闭合 |

### Negative Prompt 固定项

```
voiceover, narration, exaggerated expressions, dramatic gestures,
text overlay, subtitle, caption, camera zoom, camera push, background music,
dark skin, yellow skin, warm color cast,
foggy, hazy, soft focus, atmospheric haze, washed out, blurry
```

---

## 自审清单（生成后、给用户看前）

### 硬标准（失败→静默重跑，最多2次）

- [ ] 头巾颜色与三视图一致（V5 三视图 = 白色）
- [ ] 服装与三视图一致（白色蕾丝上衣）
- [ ] 光影风格：窗帘柔和侧光，无刺眼直射光或平板 studio 光
- [ ] 手部解剖正确，无多余手指/漂浮肢体
- [ ] 构图：半身 9:16，不裁头顶，不露腰以下过多
- [ ] **音频（Veo视频专项）**：听音频——是角色在说话（口播）还是像配音员读稿（旁白）？旁白=直接重跑。数据类台词尤其容易旁白化

### 软标准（通过后附一句评语给用户）

- [ ] 人脸与 Kirana 东南亚华裔特征一致
- [ ] 气质：从容，不表演，不夸张——"她只会笑笑"那种状态
- [ ] 整体质感清晰，自然光感，非广告棚感

---

## 输出路径规范

```
首尾帧：~/Desktop/Veirfoo_frames/[项目]_S[编号]_[first/last]_v[版本].jpg
视频：  ~/Desktop/Veirfoo_frames/[项目]_S[编号]_v[版本].mp4
完整版：~/Desktop/Veirfoo_frames/[项目]_complete_v[版本].mp4
```

---

## V1 验证通过的场景记录

> 可作为同类视频的起点参考

| 段落 | 动作 | 台词（词数） | 备注 |
|------|------|------------|------|
| S1 | 看手机→抬头 | 18词 | 开场钩子，自然 |
| S2 | 坐沙发讲解 | ~22词 | 中段科普 |
| S3 | 坐沙发讲解 | ~22词 | 中段科普 |
| S4 | 触脸→手势 | ~27词（偏多，可压） | 最难复现，光影关键 |
| S5 | 持面膜展示 | 21词 | 产品出场 |
| S6 | 坐沙发讲解 | 28词 | 情感共鸣段 |
| S7 | 指向镜头 CTA | 16词 | 结尾留白感好 |
