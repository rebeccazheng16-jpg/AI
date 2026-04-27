"""
Kirana 数字人视频 — 场景提示词模板库
scene_prompts.py

设计原则：
  - {台词} 是唯一变量，动作/构图/场景全部硬编码
  - 角色外观完全由首尾帧图片决定，提示词里零外观描述
  - 换角色（Kirana→Yuki→Hoa）= 只换首尾帧的参考图，提示词原文不变

使用示例：
    from scene_prompts import build_prompt, build_veo_cmd, CHARACTERS, NEGATIVE_PROMPT

    # 用默认台词生成提示词
    prompt = build_prompt("02_S1")

    # 换自定义台词
    prompt = build_prompt("02_S1", dialogue="你的印尼语台词")

    # 打印完整可执行命令
    print(build_veo_cmd("02_S1", output_name="02_S1_v2"))
"""

import os

# ─────────────────────────────────────────────────────────────────────────────
# 场景通用结构（所有 scene 共用，不可改）
# ─────────────────────────────────────────────────────────────────────────────

SCENE_PREFIX = (
    "Woman on cream ivory sofa by a window with sheer curtains, "
    "soft natural side light, bright airy cream interior, soft bokeh background. She "
)

DIALOGUE_WRAPPER = (
    "speaks naturally and conversationally as if telling a close friend: '{dialogue}'."
)

SCENE_SUFFIX = (
    "Calm serene wealthy young woman, subtle refined expressions, gentle composed demeanor. "
    "Minimal natural gestures, NOT exaggerated. Fixed camera, no movement. "
    "Half-body portrait, 9:16 vertical. "
    "Anatomically correct, exactly two hands, no extra limbs, "
    "no extra fingers, no deformed hands, no floating limbs."
)

NEGATIVE_PROMPT = (
    "voiceover, narration, documentary style, announcement voice, off-screen narrator, "
    "statistics reading, exaggerated expressions, dramatic gestures, theatrical performance, "
    "text overlay, subtitle, caption, camera zoom, camera push, background music, "
    "dark skin, yellow skin, warm color cast, foggy, hazy, soft focus, washed out, blurry"
)

# ─────────────────────────────────────────────────────────────────────────────
# 角色参考图（换角色只改这里，提示词原文不变）
# 用途：给 nano-banana-image-gen 生成首尾帧时传入的 -r 参数
# ─────────────────────────────────────────────────────────────────────────────

CHARACTERS = {
    "Kirana": os.path.expanduser("~/Desktop/模特公式图/Kirana/Kirana_chanel_turnaround_v2.jpg"),
    "Yuki":   os.path.expanduser("~/Desktop/模特公式图/Yuki/Yuki_turnaround.jpg"),
    "Yuna":   os.path.expanduser("~/Desktop/模特公式图/Yuna/Yuna_turnaround.jpg"),
    "Hoa":    os.path.expanduser("~/Desktop/模特公式图/Hoa/Hoa_turnaround.jpg"),
    "Lily":   os.path.expanduser("~/Desktop/模特公式图/Lily/Lily_turnaround.jpg"),
}

# ─────────────────────────────────────────────────────────────────────────────
# 场景模板
# 每个 scene：action（硬编码）+ default_dialogue（可被覆盖）+ 帧路径 + 参数
# ─────────────────────────────────────────────────────────────────────────────

_02 = os.path.expanduser("~/Desktop/脚本视频生成/02_韩国PDRN/02_韩国PDRN")
_T3 = os.path.expanduser("~/Desktop/脚本视频生成/T3_闺蜜安利型")

SCENE_TEMPLATES = {

    # ── 脚本02《韩国皮肤科最火的成分》S1-S4 ──────────────────────────────────
    # 35秒 | 口播→手持→上脸→口播 | CTA: 'PDRN' | 数据: 黄度-31%

    "02_S1": {
        # 场景：开场钩子，直视镜头，快节奏
        "action": (
            "sits with quiet knowing posture, one hand resting gently on her knee, "
            "looking directly at camera with subtle knowing expression,"
        ),
        "default_dialogue": (
            "Bahan paling laris di klinik kulit Korea? PDRN. "
            "Antriannya tiga bulan, sekali suntik jutaan. "
            "Tapi sekarang nggak perlu ke Korea."
        ),
        "first_frame": f"{_02}/02_S1_first.jpg",
        "last_frame":  f"{_02}/02_S1_last.jpg",
        "duration": 8, "resolution": "720p",
    },

    "02_S2": {
        # 场景：手持银管介绍成分
        "action": (
            "holds up a silver cylindrical tube at chest height, "
            "calm confident expression, looking at camera,"
        ),
        "default_dialogue": (
            "VEIRFOO Salmon Mask — PDRN dari DNA salmon, "
            "persis sumbernya sama dengan klinik Korea. "
            "Plus 500D micro-collagen dan 8D hyaluronic acid. Satu tube ada semua."
        ),
        "first_frame": f"{_02}/02_S2_first.jpg",
        "last_frame":  f"{_02}/02_S2_last.jpg",
        "duration": 8, "resolution": "720p",
    },

    "02_S3": {
        # 场景：上脸展示+数据 | ⚠️ 数字类台词易触发旁白，已用对话包裹+防旁白neg
        "action": (
            "gently touches her cheek with fingertips, "
            "slight forward lean, composed satisfied expression,"
        ),
        "default_dialogue": (
            "Empat belas hari warna kuning berkurang tiga puluh satu persen — "
            "ini bukan klaim iklan, ini hasil uji klinis manusia pihak ketiga."
        ),
        "first_frame": f"{_02}/02_S3_first.jpg",
        "last_frame":  f"{_02}/02_S3_last.jpg",
        "duration": 8, "resolution": "720p",
    },

    "02_S4": {
        # 场景：结尾CTA，手持产品
        "action": (
            "holds up a silver cylindrical tube at chest height, "
            "looking at camera with composed confident expression,"
        ),
        "default_dialogue": (
            "Satu tube bahannya setara satu treatment klinik Korea. "
            "Made in Korea, BPOM certified. "
            "Komen 'PDRN' aku kirim info produknya."
        ),
        "first_frame": f"{_02}/02_S4_first.jpg",
        "last_frame":  f"{_02}/02_S4_last.jpg",
        "duration": 8, "resolution": "720p",
    },

    # ── T3《闺蜜安利型》S1-S9 ────────────────────────────────────────────────
    # 62秒总长 | 全口播结构 | 无CTA关键词（安利型）

    "T3_S1": {
        # 场景：看手机→温和抬头，眼神好笑不惊讶
        "action": (
            "looking down at vivid orange iPhone 17 Pro Max in hands with a slight smile, "
            "then gently lowers the phone and looks up at camera with composed knowing expression,"
        ),
        "default_dialogue": (
            "Guys, udah 5 orang tanya aku pakai apa buat kulit aku."
        ),
        "props": [os.path.expanduser("~/Desktop/model/props_iPhone17Pro_orange.png")],
        "first_frame": f"{_T3}/T3_S1_first_v3.png",
        "last_frame":  f"{_T3}/T3_S1_last_v8.png",
        "duration": 6, "resolution": "720p",
    },

    "T3_S2": {
        # 场景：轻耸肩淡淡笑，优雅欲言又止
        "action": (
            "sits with subtle composed shrug, light knowing smile, "
            "one hand lightly raised as if about to share a secret,"
        ),
        "default_dialogue": (
            "Sebenernya nggak mau bilang, tapi karena udah banyak yang tanya..."
        ),
        "first_frame": f"{_T3}/T3_S2_first.png",
        "last_frame":  f"{_T3}/T3_S2_last.png",
        "duration": 6, "resolution": "720p",
    },

    "T3_S3": {
        # 场景：从腿上包里掏出银管举起（包始终在腿上）
        "action": (
            "reaches into a handbag resting on her lap and lifts up "
            "a silver cylindrical tube at chest height — handbag stays on her lap — "
            "composed confident expression,"
        ),
        "default_dialogue": (
            "Ini dia rahasianya — masker dari Veirfoo."
        ),
        "first_frame": f"{_T3}/T3_S3_first_v5.png",
        "last_frame":  f"{_T3}/T3_S3_last_v5.png",
        "duration": 8, "resolution": "1080p",
    },

    "T3_S4": {
        # 场景：涂脸（成膜前阶段）
        "action": (
            "gently applies product to her cheek with fingertips, "
            "calm composed expression,"
        ),
        "default_dialogue": (
            "Aku pakai ini tiap malam, lima belas menit sebelum tidur."
        ),
        "first_frame": f"{_T3}/T3_S4_first_v4.png",
        "last_frame":  f"{_T3}/T3_S4_last_v5.png",
        "duration": 8, "resolution": "1080p",
    },

    "T3_S5": {
        # 场景：成膜后懒洋洋刷手机→放下小憩
        "action": (
            "lounges on sofa scrolling on vivid orange iPhone 17 Pro Max, "
            "then lowers phone with calm content expression,"
        ),
        "default_dialogue": (
            "Dan rasanya kayak jelly dingin gitu di muka. Nggak lengket, nggak berat."
        ),
        "props": [os.path.expanduser("~/Desktop/model/props_iPhone17Pro_orange.png")],
        "first_frame": f"{_T3}/T3_S5_first_v5.png",
        "last_frame":  f"{_T3}/T3_S5_last_v4.png",
        "duration": 8, "resolution": "1080p",
    },

    "T3_S6": {
        # 场景：晨光素颜，轻触脸颊，满足笑
        "action": (
            "gently touches her cheek with one fingertip, "
            "subtle satisfied smile, soft morning light quality,"
        ),
        "default_dialogue": (
            "Besok paginya, muka aku berasa jauh lebih kenyal dan cerah."
        ),
        "first_frame": f"{_T3}/T3_S6_first.png",
        "last_frame":  f"{_T3}/T3_S6_last_v4.png",
        "duration": 6, "resolution": "720p",
    },

    "T3_S7": {
        # 场景：手持产品像跟闺蜜说悄悄话
        "action": (
            "holds up a silver cylindrical tube at chest level, "
            "leaning slightly toward camera with quiet intimate expression "
            "as if sharing a secret with a close friend,"
        ),
        "default_dialogue": (
            "Serius deh, ini beneran ngebantu kulit aku. Bukan lebay."
        ),
        "first_frame": f"{_T3}/T3_S7_first_v4.png",
        "last_frame":  f"{_T3}/T3_S7_last_v4.png",
        "duration": 8, "resolution": "1080p",
    },

    "T3_S8": {
        # 场景：低头欣赏银管→从容抬起展示
        "action": (
            "looks down at a silver cylindrical tube in her hands, "
            "then slowly raises it to chest height with calm focused expression,"
        ),
        "default_dialogue": (
            "Ada DNA salmon, kolagen, aman, dan nggak mahal."
        ),
        "first_frame": f"{_T3}/T3_S8_first_v4.png",
        "last_frame":  f"{_T3}/T3_S8_last_v5.png",
        "duration": 6, "resolution": "720p",
    },

    "T3_S9": {
        # 场景：温柔指向镜头，端庄露齿笑
        "action": (
            "raises one finger toward camera with refined gesture, "
            "gentle composed smile,"
        ),
        "default_dialogue": (
            "Kalau mau tau lebih, link di bio ya!"
        ),
        "first_frame": f"{_T3}/T3_S9_first_v4.png",
        "last_frame":  f"{_T3}/T3_S9_last_v4.png",
        "duration": 6, "resolution": "720p",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────────────────────────────────────

def build_prompt(scene_key: str, dialogue: str = None) -> str:
    """拼装 Veo 正向提示词。dialogue 留空则用默认台词。"""
    t = SCENE_TEMPLATES[scene_key]
    dlg = dialogue if dialogue is not None else t["default_dialogue"]
    return (
        f"{SCENE_PREFIX}"
        f"{t['action']} "
        f"{DIALOGUE_WRAPPER.format(dialogue=dlg)} "
        f"{SCENE_SUFFIX}"
    )


def build_veo_cmd(
    scene_key: str,
    dialogue: str = None,
    output_dir: str = None,
    output_name: str = None,
    first_frame: str = None,
    last_frame: str = None,
) -> str:
    """
    生成完整 veo_video_gen.py 调用命令字符串，可直接粘贴执行。

    first_frame / last_frame 可覆盖默认值——换角色时传入新角色的帧路径，
    提示词原文不变。
    """
    t = SCENE_TEMPLATES[scene_key]
    prompt = build_prompt(scene_key, dialogue)
    ff = first_frame or t["first_frame"]
    lf = last_frame or t["last_frame"]
    out_dir = output_dir or os.path.dirname(ff)
    name = output_name or f"{scene_key}_v1"

    return (
        f'python3 ~/.claude/skills/veo-video-gen/scripts/veo_video_gen.py \\\n'
        f'  "{prompt}" \\\n'
        f'  -i "{ff}" -l "{lf}" \\\n'
        f'  -r {t["resolution"]} -d {t["duration"]} -a "9:16" \\\n'
        f'  --negative-prompt "{NEGATIVE_PROMPT}" \\\n'
        f'  -n "{name}" -o "{out_dir}"'
    )


# ─────────────────────────────────────────────────────────────────────────────
# 换角色说明
# ─────────────────────────────────────────────────────────────────────────────
#
# Step 1：用新角色三视图生成首尾帧（nano-banana-image-gen）
#   python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py \
#     "[场景描述，不写外观]" \
#     -r CHARACTERS["Yuki"] \
#     -a "9:16" -s "4K" -n "T3_S1_Yuki_first" -o "~/Desktop/脚本视频生成/T3_闺蜜安利型/"
#
# Step 2：用新帧路径调 build_veo_cmd，提示词原文不改
#   cmd = build_veo_cmd(
#       "T3_S1",
#       first_frame="~/Desktop/脚本视频生成/T3_闺蜜安利型/T3_S1_Yuki_first.jpg",
#       last_frame="~/Desktop/脚本视频生成/T3_闺蜜安利型/T3_S1_Yuki_last.jpg",
#       output_name="T3_S1_Yuki_v1",
#   )
#
# ─────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    import sys
    scene = sys.argv[1] if len(sys.argv) > 1 else "02_S1"
    print("=" * 70)
    print(f"Scene: {scene}")
    print("=" * 70)
    print("\n[Prompt]\n")
    print(build_prompt(scene))
    print("\n[Veo Command]\n")
    print(build_veo_cmd(scene, output_name=f"{scene}_v1"))
