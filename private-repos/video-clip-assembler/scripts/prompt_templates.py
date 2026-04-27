"""
招商视频（Tulandut 代理商证言）prompt 模板。
服务端专用，前端不可见。用户仅看到可编辑的台词部分。
"""

import random

# ── 段落定义 ──
SEGMENT_TYPES = [
    {"idx": 0, "type": "ai_firstlast", "label_zh": "S1 过去的辛苦", "label_id": "S1 Past Struggle", "duration": 8},
    {"idx": 1, "type": "ai_firstlast", "label_zh": "S2 转折+现在", "label_id": "S2 Turning Point", "duration": 8},
    {"idx": 2, "type": "ai_static", "label_zh": "S3 第一笔收入", "label_id": "S3 First Earning", "duration": 8},
    {"idx": 3, "type": "ai_static", "label_zh": "S4 小成就", "label_id": "S4 Small Wins", "duration": 8},
    {"idx": 4, "type": "ai_static", "label_zh": "S5 女性赋权CTA", "label_id": "S5 Empowerment CTA", "duration": 8},
]

# ── 默认台词 ──
DEFAULT_SCRIPTS = [
    {
        "zh": "以前我凌晨4点起床，给孩子准备、伺候老公，上一整天班。累死了，但收入永远就那样。",
        "id": "Dulu aku bangun jam 4 pagi, siapin anak, siapin suami, terus kerja seharian. Capek banget, tapi penghasilan tetap segitu-gitu aja.",
    },
    {
        "zh": "后来朋友拉我加入 Tulandut……现在？我有了额外收入，在家就能赚。",
        "id": "Terus temen aku ajak gabung Tulandut... sekarang? Aku punya penghasilan tambahan, dari rumah aja.",
    },
    {
        "zh": "第一次拿到佣金的时候，我用那笔钱给女儿买了她想要很久的书包。她开心得跳起来……那一刻我觉得，值了。",
        "id": "Pertama kali dapet komisi, aku beliin anak perempuanku tas sekolah yang dia udah lama mau. Dia seneng banget sampai lompat-lompat... waktu itu aku ngerasa, worth it banget.",
    },
    {
        "zh": "现在每个月多出来的收入虽然不大，但够给孩子充网费、买零食、报个数学补习班。这些小事，以前都要开口问老公要。",
        "id": "Sekarang penghasilan tambahan tiap bulan emang belum besar, tapi cukup buat isi kuota anak, beliin jajan, daftarin les matematika. Hal-hal kecil gini, dulu harus minta ke suami.",
    },
    {
        "zh": "女人有自己的收入，说话都更有底气。不用多，够让你在arisan的时候抬得起头就行。加入 Tulandut，自己试试看。",
        "id": "Perempuan punya penghasilan sendiri, ngomong aja lebih pede. Nggak perlu banyak, cukup buat kamu bisa ikut arisan dengan tenang. Gabung Tulandut, coba sendiri deh.",
    },
]

# ── 变量池（每次随机组合） ──

# ── 面部特征池（每次随机组合，产生不同的脸） ──
FACE_POOL = [
    {
        "zh": "35岁爪哇女性，圆脸，丰满嘴唇，偏黑肤色",
        "en": "a 35-year-old Javanese Indonesian Muslim woman with warm brown sawo matang skin, round face, broad gentle nose, full lips, dark brown eyes, medium build with soft rounded shoulders",
        "voice": "声音温暖沉稳，像邻居大姐在聊天",
    },
    {
        "zh": "40岁巽他女性，瓜子脸，纤细鼻梁，棕褐肤色",
        "en": "a 40-year-old Sundanese Indonesian Muslim woman with warm tan skin, oval face with defined cheekbones, slim nose bridge, almond-shaped dark eyes, slightly thin build",
        "voice": "声音略带沙哑，像一个见过世面的妈妈",
    },
    {
        "zh": "33岁爪哇女性，方脸，厚嘴唇，深棕肤色",
        "en": "a 33-year-old Javanese Indonesian Muslim woman with deep brown skin, square jaw, thick lips, wide-set dark eyes with heavy lids, sturdy medium-large build with broad shoulders",
        "voice": "声音有力但温柔，像市场里最会讲价的阿姨",
    },
    {
        "zh": "38岁马都拉女性，长脸，高颧骨，黄褐肤色",
        "en": "a 38-year-old Madurese Indonesian Muslim woman with golden-brown skin, long face with high cheekbones, narrow eyes, thin lips, lean medium build",
        "voice": "声音平和内敛，像一个安静但坚定的母亲",
    },
    {
        "zh": "42岁巴达维女性，圆润脸型，宽鼻，偏浅棕肤色",
        "en": "a 42-year-old Betawi Indonesian Muslim woman with light brown skin, round plump face, wide nose, large expressive dark eyes with crow's feet, plump build with soft arms",
        "voice": "声音爽朗直率，像菜市场里热情招呼你的大姐",
    },
    {
        "zh": "36岁米南加保女性，心形脸，小嘴，中等棕肤色",
        "en": "a 36-year-old Minangkabau Indonesian Muslim woman with medium brown skin, heart-shaped face, small mouth, delicate features, petite build with narrow shoulders",
        "voice": "声音柔和细腻，像在轻轻讲秘密",
    },
]
VOICE_DESC = "声音温暖成熟，像一个有生活阅历的妈妈在聊天"

# ── 头巾颜色池（戴法统一全包裹，只随机颜色） ──
HIJAB_POOL = [
    {"zh": "淡粉色", "en": "dusty rose"},
    {"zh": "米白色", "en": "cream ivory"},
    {"zh": "薄荷绿", "en": "sage mint"},
    {"zh": "浅蓝色", "en": "powder blue"},
    {"zh": "驼色", "en": "warm camel"},
    {"zh": "珊瑚橘", "en": "coral orange"},
    {"zh": "丁香紫", "en": "lavender lilac"},
    {"zh": "深棕色", "en": "chocolate brown"},
    {"zh": "橄榄绿", "en": "olive green"},
    {"zh": "酒红色", "en": "burgundy wine"},
    {"zh": "芥末黄", "en": "mustard gold"},
    {"zh": "藏蓝色", "en": "dark navy"},
]

# ── 服装（只指定颜色+材质，款式说"印尼穆斯林得体服装"让 Gemini 自由发挥） ──
OUTFIT_COLOR_POOL = [
    {"zh": "翠绿色", "en": "emerald green"},
    {"zh": "酒红色", "en": "burgundy wine"},
    {"zh": "奶白色", "en": "cream white"},
    {"zh": "深蓝色", "en": "navy blue"},
    {"zh": "藕粉色", "en": "mauve pink"},
    {"zh": "浅灰色", "en": "light grey"},
    {"zh": "香槟色", "en": "champagne"},
    {"zh": "墨绿色", "en": "dark green"},
    {"zh": "宝蓝色", "en": "royal blue"},
    {"zh": "焦糖棕", "en": "caramel brown"},
    {"zh": "浅卡其", "en": "light khaki"},
    {"zh": "黑色", "en": "black"},
    {"zh": "珊瑚色", "en": "coral"},
    {"zh": "松石绿", "en": "teal"},
]

OUTFIT_FABRIC_POOL = [
    {"zh": "棉质", "en": "cotton"},
    {"zh": "棉麻", "en": "cotton-linen blend"},
    {"zh": "涤纶", "en": "polyester"},
    {"zh": "针织", "en": "jersey knit"},
    {"zh": "雪纺", "en": "chiffon"},
]

# ── 首饰（日常简朴，UMKM/职场女性水平） ──
JEWELRY_POOL = [
    {"zh": "小金耳钉", "en": "tiny gold stud earrings"},
    {"zh": "无首饰", "en": "no visible jewelry"},
    {"zh": "简单手表", "en": "a simple wristwatch"},
    {"zh": "细金链项链", "en": "a thin gold chain necklace"},
    {"zh": "小圆耳环", "en": "small simple hoop earrings"},
    {"zh": "塑料发夹", "en": "a simple plastic hair clip under hijab"},
]

# ── 场景（印尼普通家庭/小店，iPhone 手持录制质感） ──
SETTING_POOL = [
    {
        "zh": "整洁的印尼普通家庭客厅，batik靠垫的布沙发",
        "en": "a simple fabric sofa with colorful batik throw pillows in a tidy Indonesian home living room with beige ceramic tile floor, off-white walls with family photos, a wooden coffee table with a glass of sweet tea, white curtains on a window with natural daylight from the left",
    },
    {
        "zh": "印尼家庭前廊（teras），塑料椅子旁边有盆栽",
        "en": "a plastic chair on the front terrace (teras) of a modest Indonesian home with potted plants, a small side table, tiled floor, the front yard visible in the background with warm natural daylight",
    },
    {
        "zh": "小warung店铺后面的休息角，简单木凳",
        "en": "a simple wooden stool behind a small Indonesian warung (shop) counter, shelves with daily goods in the background, fluorescent ceiling light mixed with natural daylight from the open shopfront on the left",
    },
    {
        "zh": "简单的卧室角落，铁架床旁边的塑料椅",
        "en": "a plastic chair next to a simple bed with a floral bedsheet in a modest Indonesian bedroom, plain painted walls with a calendar and small mirror, ceramic tile floor, soft natural light from a window with thin curtains on the left",
    },
    {
        "zh": "印尼家庭餐厅，木桌旁的椅子",
        "en": "a wooden dining chair at a simple dining table in an Indonesian family home, a thermos and glasses on the table, tiled floor, off-white walls, a hanging clock, natural daylight from a side window on the left",
    },
    {
        "zh": "明亮的印尼中产客厅，米色布沙发",
        "en": "a beige fabric sofa with batik cushions in a bright clean Indonesian middle-class home living room with ceramic tile floors, a simple wooden shelf with books and framed children's photos, white curtains filtering soft natural light from the left, a small potted palm nearby",
    },
]

# ── TTS 发音修正映射（Seedance prompt 专用，不影响字幕） ──
TTS_PRONUNCIATION_MAP = {
    "cewek": "cheh-we",
    "cuan": "chuan",
    "capek": "chah-pe",
    "cape": "qia-pe",
    "capai": "chah-pai",
    "cukup": "chu-kup",
    "cocok": "cho-cho",
    "coba": "cho-ba",
    "cerita": "cheh-ri-ta",
    "yuk": "ayo",
    "yu": "ayo",
}


def fix_tts_pronunciation(text):
    """Replace Indonesian words with phonetic spelling for Seedance TTS.
    Only used in Seedance prompts, NOT in subtitles."""
    import re
    result = text
    for word, phonetic in TTS_PRONUNCIATION_MAP.items():
        result = re.sub(r'\b' + word + r'\b', phonetic, result, flags=re.IGNORECASE)
    return result


SCENE_BASE = "写实风格，自然窗光从左侧照入"
SCENE_SUFFIX = "固定机位，iPhone原相机画质。没有背景音乐，没有环境音效，只有纯净的人声。语调平稳自然，不要激动，不要高音，不要夸张，像跟朋友聊天一样平静地说话。"


def randomize_variables():
    """随机抽取一组外观变量。面部/头巾/服装/首饰/场景全部独立随机。"""
    hijab_color = random.choice(HIJAB_POOL)
    outfit_color = random.choice(OUTFIT_COLOR_POOL)
    outfit_fabric = random.choice(OUTFIT_FABRIC_POOL)
    face = random.choice(FACE_POOL)
    return {
        "hijab": {"zh": f"{hijab_color['zh']}头巾", "en": f"{hijab_color['en']} hijab"},
        "face": face["zh"],
        "face_en": face["en"],
        "voice": face.get("voice", VOICE_DESC),
        "outfit": {
            "zh": f"{outfit_color['zh']}{outfit_fabric['zh']}印尼穆斯林得体服装",
            "en": f"a modest Indonesian Muslim outfit in {outfit_color['en']} {outfit_fabric['en']}",
        },
        "jewelry": random.choice(JEWELRY_POOL),
        "setting": random.choice(SETTING_POOL),
    }


def build_seedance_prompt(segment_idx, user_script_id, variables=None):
    """
    拼接完整 Seedance prompt（对用户不可见）。
    segment_idx: 0-4
    user_script_id: 用户确认的印尼语台词
    variables: randomize_variables() 的返回值
    """
    if variables is None:
        variables = randomize_variables()

    v = variables
    hijab_zh = v["hijab"]["zh"]
    outfit_zh = v["outfit"]["zh"]
    jewelry_zh = v["jewelry"]["zh"]
    face = v["face"]
    voice = v["voice"]

    # Fix pronunciation for TTS only — subtitles keep original text
    tts_text = fix_tts_pronunciation(user_script_id)

    setting_zh = v['setting']['zh']

    if segment_idx == 0:
        return f"""{SCENE_BASE}，{setting_zh}。一个{face}，{voice}，坐在椅子上，戴着{hijab_zh}，穿{outfit_zh}，佩戴{jewelry_zh}。她的声音不是年轻女孩的清脆声线。她像在跟老朋友诉苦一样缓缓地说："{tts_text}" 表情从回忆中的沉思逐渐转为无奈的淡笑，手势自然轻柔，{SCENE_SUFFIX}"""

    elif segment_idx == 1:
        return f"""{SCENE_BASE}，{setting_zh}。同一个女人，{face}，{voice}，戴着{hijab_zh}，穿{outfit_zh}。她的声音依然平静，语气里多了一点点轻松，语速保持自然不加快。她说："{tts_text}" 说到"sekarang"时嘴角微微上扬，{SCENE_SUFFIX}"""

    elif segment_idx == 2:
        return f"""{SCENE_BASE}，{setting_zh}。照片中的女人坐着，自然地对着镜头说话。{face}，{voice}，语气轻松随意，像在arisan聚会上跟姐妹聊天。她说："{tts_text}" 说到"lompat-lompat"时忍不住笑了一下，眼角有真实的笑纹。{SCENE_SUFFIX}"""

    elif segment_idx == 3:
        return f"""{SCENE_BASE}，{setting_zh}。照片中的女人坐着，一只手轻轻比划。{face}，{voice}，语气平和真实，像在跟邻居分享生活小变化。她说："{tts_text}" 说到"minta ke suami"时微微低头笑了一下，不是苦笑，是释然的笑。{SCENE_SUFFIX}"""

    elif segment_idx == 4:
        return f"""{SCENE_BASE}，{setting_zh}。照片中的女人坐着，表情温暖而诚恳。{face}，{voice}，声音始终平和温柔，不提高音量。她说："{tts_text}" 说完一只手轻放胸口，温柔地对镜头微笑。{SCENE_SUFFIX}"""

    return ""


def build_ref_image_prompt(variables=None):
    """生成参考图（定妆照）的 Nano Banana prompt。"""
    if variables is None:
        variables = randomize_variables()
    v = variables
    return f"""{FACE_EN} sitting on {v['setting']['en']}. Medium shot from waist up, casual iPhone handheld framing, natural skin texture with visible pores, no studio lighting, no artificial backdrop — this is a real wealthy Indonesian home, filmed casually on a phone. She has a warm, genuine smile, looking at someone just off-camera. She wears a {v["hijab"]["en"]} neatly wrapped covering all hair, {v["outfit"]["en"]}, {v["jewelry"]["en"]}. Natural dewy makeup. Soft natural ambient light, no flash, no color grading. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands."""


def build_first_frame_prompt(segment_idx, variables=None):
    """生成首帧图片的 Nano Banana prompt（仅 S1/S2 需要）。"""
    if variables is None:
        variables = randomize_variables()
    v = variables
    face_en = v.get("face_en", "a 35-year-old Indonesian woman")
    base = f"{face_en}, sitting on {v['setting']['en']}. Medium shot from waist up, casual iPhone handheld framing, natural skin texture with visible pores, no studio lighting, no artificial backdrop — this is a real home, filmed casually on a phone. She wears a {v['hijab']['en']} neatly wrapped covering all hair, {v['outfit']['en']}, {v['jewelry']['en']}. Natural dewy makeup. Soft natural ambient light, no flash, no color grading. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands."

    if segment_idx == 0:
        return f"{base[:-1]} resting naturally on her lap. She has a slightly reflective, thoughtful expression — about to share a personal memory, looking gently at someone just off-camera to the right. Her lips are softly closed, eyes calm but with a hint of nostalgia."
    elif segment_idx == 1:
        return f"{base} She has a slight spark in her eyes, as if about to share good news — the corner of her lips just beginning to lift, transitioning from weariness to hope."
    return base


def build_last_frame_prompt(segment_idx, variables=None):
    """生成尾帧图片的 Nano Banana prompt（仅 S1/S2 需要）。"""
    if variables is None:
        variables = randomize_variables()
    v = variables
    face_en = v.get("face_en", "a 35-year-old Indonesian woman")
    base = f"{face_en}, sitting on {v['setting']['en']}. Medium shot from waist up, casual iPhone handheld framing, natural skin texture with visible pores, no studio lighting, no artificial backdrop — this is a real home, filmed casually on a phone. She wears a {v['hijab']['en']} neatly wrapped covering all hair, {v['outfit']['en']}, {v['jewelry']['en']}. Natural dewy makeup. Soft natural ambient light, no flash, no color grading. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands."

    if segment_idx == 0:
        return f"{base[:-1]}, one hand resting on armrest the other on her lap. She has just finished saying something bittersweet — a gentle resigned half-smile, eyes slightly downcast, exhaling softly as if recalling exhausting days."
    elif segment_idx == 1:
        return f"{base} She has a quiet, confident smile — the expression of someone whose life has genuinely improved. Eyes warm and steady, posture relaxed but dignified."
    return base


def build_chain_frame_prompt(chain_idx, variables=None):
    """生成链式帧提示词。4帧串联生成3段视频：F0→F1, F1→F2, F2→F3。
    chain_idx: 0=S1起始, 1=S1结束/S2起始, 2=S2结束/S3起始, 3=S3结束
    """
    if variables is None:
        variables = randomize_variables()
    v = variables
    face_en = v.get("face_en", "a 35-year-old Indonesian woman")
    base = f"{face_en}, sitting on {v['setting']['en']}. Medium shot from waist up, casual iPhone handheld framing, natural skin texture with visible pores, no studio lighting, no artificial backdrop — this is a real home, filmed casually on a phone. She wears a {v['hijab']['en']} neatly wrapped covering all hair, {v['outfit']['en']}, {v['jewelry']['en']}. Natural dewy makeup. Soft natural ambient light, no flash, no color grading. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands."

    if chain_idx == 0:
        # S1 起始：回忆往事
        return f"{base[:-1]} resting naturally on her lap. She has a slightly reflective, thoughtful expression — about to share a personal memory, looking gently at someone just off-camera to the right. Her lips are softly closed, eyes calm but with a hint of nostalgia."
    elif chain_idx == 1:
        # S1 结束 / S2 起始：从疲惫转向希望
        return f"{base[:-1]}, one hand resting on armrest the other on her lap. She has just finished recalling exhausting days — a gentle resigned half-smile transitioning into a spark of hope, eyes beginning to brighten."
    elif chain_idx == 2:
        # S2 结束 / S3 起始：希望变为自信
        return f"{base} She has a quiet, confident smile — the expression of someone whose life has genuinely improved. Eyes warm and steady, posture relaxed but dignified, about to share practical advice."
    elif chain_idx == 3:
        # S3 结束：轻松随意
        return f"{base} She looks relaxed and natural, as if chatting casually with a close friend. Gentle smile, one hand gesturing lightly, calm and approachable demeanor."
    return base


def get_segment_info():
    """返回前端展示用的段落信息（不含 prompt）。"""
    return [
        {
            "idx": s["idx"],
            "type": s["type"],
            "label_zh": s["label_zh"],
            "label_id": s["label_id"],
            "duration": s["duration"],
            "default_zh": DEFAULT_SCRIPTS[s["idx"]]["zh"],
            "default_id": DEFAULT_SCRIPTS[s["idx"]]["id"],
        }
        for s in SEGMENT_TYPES
    ]
