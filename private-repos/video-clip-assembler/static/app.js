// === TikTok 违禁词数据库 ===
// 来源：~/.claude/skills/tiktok-content-policy/references/
const BANNED_WORDS = [
  // ── 绝对化用语 (Absolute Claims) ──
  { word: 'pertama', cat: 'absolute', lang: 'id' },
  { word: 'satu-satunya', cat: 'absolute', lang: 'id' },
  { word: 'terbaik', cat: 'absolute', lang: 'id' },
  { word: 'termurah', cat: 'absolute', lang: 'id' },
  { word: 'nomor satu', cat: 'absolute', lang: 'id' },
  { word: 'paling murah', cat: 'absolute', lang: 'id' },
  { word: 'paling bagus', cat: 'absolute', lang: 'id' },
  { word: 'paling ampuh', cat: 'absolute', lang: 'id' },
  { word: 'terlaris', cat: 'absolute', lang: 'id' },
  { word: 'best seller', cat: 'absolute', lang: 'en' },
  { word: 'number one', cat: 'absolute', lang: 'en' },
  { word: '第一', cat: 'absolute', lang: 'zh' },
  { word: '唯一', cat: 'absolute', lang: 'zh' },
  { word: '最好', cat: 'absolute', lang: 'zh' },
  { word: '最强', cat: 'absolute', lang: 'zh' },
  { word: '最低价', cat: 'absolute', lang: 'zh' },
  { word: '全网最低', cat: 'absolute', lang: 'zh' },
  { word: '全网最', cat: 'absolute', lang: 'zh' },
  { word: '必抢', cat: 'absolute', lang: 'zh' },
  { word: '清仓', cat: 'absolute', lang: 'zh' },

  // ── 医疗声称 (Medical Claims) ──
  { word: 'menyembuhkan', cat: 'medical', lang: 'id' },
  { word: 'mengobati', cat: 'medical', lang: 'id' },
  { word: 'obat', cat: 'medical', lang: 'id' },
  { word: 'sembuh', cat: 'medical', lang: 'id' },
  { word: 'menyembuh', cat: 'medical', lang: 'id' },
  { word: 'permanen', cat: 'medical', lang: 'id' },
  { word: 'selamanya', cat: 'medical', lang: 'id' },
  { word: 'farmakologi', cat: 'medical', lang: 'id' },
  { word: 'imunologi', cat: 'medical', lang: 'id' },
  { word: 'metabolisme', cat: 'medical', lang: 'id' },
  { word: 'cure', cat: 'medical', lang: 'en' },
  { word: 'permanent', cat: 'medical', lang: 'en' },
  { word: '治愈', cat: 'medical', lang: 'zh' },
  { word: '治疗', cat: 'medical', lang: 'zh' },
  { word: '根治', cat: 'medical', lang: 'zh' },
  { word: '药效', cat: 'medical', lang: 'zh' },
  { word: '永久', cat: 'medical', lang: 'zh' },
  { word: '药理学', cat: 'medical', lang: 'zh' },
  { word: '免疫学', cat: 'medical', lang: 'zh' },
  { word: '代谢效应', cat: 'medical', lang: 'zh' },

  // ── 美妆红线 (Beauty Red Lines) ──
  { word: 'menghilangkan jerawat', cat: 'beauty', lang: 'id' },
  { word: 'menghilangkan kerutan', cat: 'beauty', lang: 'id' },
  { word: 'menghilangkan flek', cat: 'beauty', lang: 'id' },
  { word: 'menghilangkan bekas', cat: 'beauty', lang: 'id' },
  { word: 'memutihkan', cat: 'beauty', lang: 'id' },
  { word: 'pemutih', cat: 'beauty', lang: 'id' },
  { word: 'bleaching', cat: 'beauty', lang: 'id' },
  { word: 'anti-aging', cat: 'beauty', lang: 'en' },
  { word: 'anti aging', cat: 'beauty', lang: 'en' },
  { word: 'mengurangi melanin', cat: 'beauty', lang: 'id' },
  { word: 'menumbuhkan rambut', cat: 'beauty', lang: 'id' },
  { word: 'remove acne', cat: 'beauty', lang: 'en' },
  { word: 'remove wrinkles', cat: 'beauty', lang: 'en' },
  { word: 'eliminate wrinkles', cat: 'beauty', lang: 'en' },
  { word: '祛痘', cat: 'beauty', lang: 'zh' },
  { word: '消除皱纹', cat: 'beauty', lang: 'zh' },
  { word: '去除皱纹', cat: 'beauty', lang: 'zh' },
  { word: '治疗脱发', cat: 'beauty', lang: 'zh' },
  { word: '美白', cat: 'beauty', lang: 'zh' },
  { word: '去除黑色素', cat: 'beauty', lang: 'zh' },
  { word: '去除痤疮', cat: 'beauty', lang: 'zh' },

  // ── 夸大承诺 (Exaggerated Promises) ──
  { word: '100% efektif', cat: 'exaggerated', lang: 'id' },
  { word: '100% ampuh', cat: 'exaggerated', lang: 'id' },
  { word: 'dijamin', cat: 'exaggerated', lang: 'id' },
  { word: 'pasti berhasil', cat: 'exaggerated', lang: 'id' },
  { word: 'langsung hilang', cat: 'exaggerated', lang: 'id' },
  { word: 'instan', cat: 'exaggerated', lang: 'id' },
  { word: 'ajaib', cat: 'exaggerated', lang: 'id' },
  { word: 'mukjizat', cat: 'exaggerated', lang: 'id' },
  { word: 'dalam sekejap', cat: 'exaggerated', lang: 'id' },
  { word: 'guaranteed', cat: 'exaggerated', lang: 'en' },
  { word: '100% effective', cat: 'exaggerated', lang: 'en' },
  { word: '100%有效', cat: 'exaggerated', lang: 'zh' },
  { word: '立即见效', cat: 'exaggerated', lang: 'zh' },
  { word: '包治百病', cat: 'exaggerated', lang: 'zh' },
  { word: '保证效果', cat: 'exaggerated', lang: 'zh' },
  { word: '几天见效', cat: 'exaggerated', lang: 'zh' },

  // ── 减肥声称 (Weight Loss Claims) ──
  { word: 'menurunkan berat badan', cat: 'weight', lang: 'id' },
  { word: 'melangsingkan', cat: 'weight', lang: 'id' },
  { word: 'pelangsing', cat: 'weight', lang: 'id' },
  { word: 'pembakar lemak', cat: 'weight', lang: 'id' },
  { word: 'diet cepat', cat: 'weight', lang: 'id' },
  { word: 'kurus cepat', cat: 'weight', lang: 'id' },
  { word: 'turun berat', cat: 'weight', lang: 'id' },
  { word: 'instant weight loss', cat: 'weight', lang: 'en' },
  { word: '减肥', cat: 'weight', lang: 'zh' },
  { word: '瘦身', cat: 'weight', lang: 'zh' },
  { word: '燃烧脂肪', cat: 'weight', lang: 'zh' },
  { word: '立即减肥', cat: 'weight', lang: 'zh' },

  // ── 竞品/外部平台 (Competitor/External Platform Mentions) ──
  { word: 'shopee', cat: 'competitor', lang: 'all' },
  { word: 'lazada', cat: 'competitor', lang: 'all' },
  { word: 'tokopedia', cat: 'competitor', lang: 'all' },
  { word: 'bukalapak', cat: 'competitor', lang: 'all' },
  { word: 'whatsapp', cat: 'external', lang: 'all' },
  { word: 'hubungi wa', cat: 'external', lang: 'id' },
  { word: 'chat wa', cat: 'external', lang: 'id' },
  { word: 'add line', cat: 'external', lang: 'en' },
  { word: '加微信', cat: 'external', lang: 'zh' },

  // ── 直播禁用语 (Livestream Banned Phrases) ──
  { word: 'stok terbatas', cat: 'promo', lang: 'id' },
  { word: 'limited stock', cat: 'promo', lang: 'en' },
  { word: 'harga termurah', cat: 'promo', lang: 'id' },
  { word: 'harga terendah', cat: 'promo', lang: 'id' },
  { word: 'terakhir', cat: 'promo', lang: 'id' },
  { word: 'flash sale', cat: 'promo', lang: 'en' },
  { word: '限时特惠', cat: 'promo', lang: 'zh' },
  { word: '限时抢购', cat: 'promo', lang: 'zh' },
];

// 违禁词类别元信息
const BANNED_CATEGORIES = {
  absolute:    { zh: '绝对化用语', id: 'Klaim Absolut', en: 'Absolute Claims', color: '#e74c3c' },
  medical:     { zh: '医疗声称', id: 'Klaim Medis', en: 'Medical Claims', color: '#e74c3c' },
  beauty:      { zh: '美妆红线', id: 'Red Line Kecantikan', en: 'Beauty Red Lines', color: '#e67e22' },
  exaggerated: { zh: '夸大承诺', id: 'Klaim Berlebihan', en: 'Exaggerated Claims', color: '#e74c3c' },
  weight:      { zh: '减肥声称', id: 'Klaim Diet', en: 'Weight Loss Claims', color: '#e67e22' },
  competitor:  { zh: '竞品提及', id: 'Sebutan Kompetitor', en: 'Competitor Mention', color: '#f39c12' },
  external:    { zh: '外部引流', id: 'Pengalihan Eksternal', en: 'External Routing', color: '#f39c12' },
  promo:       { zh: '促销违规', id: 'Promosi Terlarang', en: 'Promo Violation', color: '#e67e22' },
};

/**
 * 扫描文本中的违禁词，返回匹配结果数组
 * @param {string} text - 要扫描的文本
 * @returns {Array<{word, cat, start, end}>}
 */
function scanBannedWords(text) {
  if (!text) return [];
  const lower = text.toLowerCase();
  const results = [];

  // 按词长降序排列，优先匹配长词避免子串重复
  const sorted = [...BANNED_WORDS].sort((a, b) => b.word.length - a.word.length);
  const covered = new Set();

  for (const entry of sorted) {
    const w = entry.word.toLowerCase();
    let pos = 0;
    while ((pos = lower.indexOf(w, pos)) !== -1) {
      let alreadyCovered = false;
      for (let i = pos; i < pos + w.length; i++) {
        if (covered.has(i)) { alreadyCovered = true; break; }
      }
      if (!alreadyCovered) {
        for (let i = pos; i < pos + w.length; i++) covered.add(i);
        results.push({
          word: text.substring(pos, pos + w.length),
          cat: entry.cat,
          start: pos,
          end: pos + w.length,
        });
      }
      pos += 1;
    }
  }

  results.sort((a, b) => a.start - b.start);
  return results;
}

/**
 * 将文本中的违禁词用红色 span 包裹，返回 HTML
 */
function highlightBannedWords(text, violations) {
  if (!violations.length) return escapeHtml(text);

  // 合并重叠区间
  const merged = [];
  for (const v of violations) {
    if (merged.length && v.start < merged[merged.length - 1].end) {
      merged[merged.length - 1].end = Math.max(merged[merged.length - 1].end, v.end);
      merged[merged.length - 1].cats.add(v.cat);
    } else {
      merged.push({ start: v.start, end: v.end, cats: new Set([v.cat]) });
    }
  }

  let html = '';
  let cursor = 0;
  for (const m of merged) {
    if (m.start > cursor) {
      html += escapeHtml(text.substring(cursor, m.start));
    }
    const catClass = [...m.cats].join(' ');
    const catLabel = [...m.cats].map(c => {
      const info = BANNED_CATEGORIES[c];
      return info ? (info[currentLang] || info.zh) : c;
    }).join(', ');
    html += `<span class="violation-word" data-cats="${catClass}" title="${escapeHtml(catLabel)}">${escapeHtml(text.substring(m.start, m.end))}</span>`;
    cursor = m.end;
  }
  if (cursor < text.length) {
    html += escapeHtml(text.substring(cursor));
  }
  return html;
}

// === i18n Translations ===
const I18N = {
  zh: {
    subtitle: '上传采访片段 → 转录翻译 → 勾选排序 → 自动剪辑',
    step1_title: '上传视频片段',
    upload_hint: '拖放视频文件到这里，或点击选择',
    upload_formats: '支持 mp4 / mov / webm，可多次添加',
    audio_lang: '音频语言',
    lang_id: '印尼语 (Indonesian)',
    lang_ko: '韩语 (Korean)',
    lang_ja: '日语 (Japanese)',
    lang_zh: '中文 (Chinese)',
    lang_auto: '自动检测',
    vocab_label: '专有名词（可选）',
    vocab_placeholder: '品牌名、人名等，逗号分隔。例：Veirfoo, PDRN, Tulandut',
    vocab_hint: '帮助 Gemini 准确识别不常见的词汇',
    btn_upload: '上传并开始转录',
    step2_title: '转录 + 翻译',
    status_preparing: '准备中...',
    step3_title: '勾选需要的句子',
    btn_select_all: '全选',
    btn_select_none: '全不选',
    btn_back_upload: '返回上传',
    btn_next_sort: '下一步：排序',
    step4_title: '拖拽调整顺序',
    sort_hint: '拖动片段标题调整整组顺序，拖动单句在组内/跨组移动',
    btn_back_select: '返回勾选',
    btn_next_keywords: '下一步：关键词',
    step5_title: '关键词高亮',
    keyword_desc: '选择自动分类或手动输入关键词。高亮词在字幕中放大+黄色显示。',
    chip_numbers: '数字',
    chip_money: '金额',
    chip_time: '时间',
    chip_age: '年龄',
    chip_brand: '品牌名',
    chip_emotion: '强调词',
    btn_auto_detect: '自动识别分类',
    manual_keyword_label: '或手动输入中文关键词：',
    keyword_placeholder: '例：真的, 百万, 一天',
    btn_match_keywords: '匹配关键词',
    btn_back_sort: '返回排序',
    btn_build_video: '生成视频',
    step6_title: '生成视频',
    btn_back_keywords: '返回关键词',
    stage_trimming: '裁剪片段',
    stage_concat: '拼接视频',
    stage_subtitle: '生成字幕',
    stage_burning: '烧录字幕',
    stage_compressing: '压缩输出',
    status_building: '构建中...',
    subtitle_choice_prompt: '拼接完成！是否需要自动烧录字幕？',
    btn_add_subtitle: '加字幕',
    btn_download_no_subtitle: '直接下载（不加字幕）',
    download_complete: '视频生成完成！',
    btn_download_video: '下载视频',
    // Violation check
    violation_title: '违禁词审核',
    violation_summary_clean: '未检测到违禁词',
    violation_summary_found: '检测到 {count} 处违禁词（{sentences} 句涉及）',
    violation_recheck: '重新检查',
    violation_cat_absolute: '绝对化用语',
    violation_cat_medical: '医疗声称',
    violation_cat_beauty: '美妆红线',
    violation_cat_exaggerated: '夸大承诺',
    violation_cat_weight: '减肥声称',
    violation_cat_competitor: '竞品提及',
    violation_cat_external: '外部引流',
    violation_cat_promo: '促销违规',
    violation_rule_absolute: '不得使用绝对化用语（TikTok电商/广告政策）',
    violation_rule_medical: '化妆品不得作医疗声称（TikTok全平台红线）',
    violation_rule_beauty: '不得承诺治疗/消除皮肤问题（TikTok广告+电商政策）',
    violation_rule_exaggerated: '不得使用夸大承诺用语（TikTok电商/直播政策）',
    violation_rule_weight: '不得作减肥声称（TikTok广告政策）',
    violation_rule_competitor: '直播/广告中禁止提及竞品平台（TikTok电商政策）',
    violation_rule_external: '禁止引流至站外平台（TikTok电商政策）',
    violation_rule_promo: '禁止使用制造紧迫感的促销用语（TikTok电商政策）',
    // Dynamic strings used in JS
    uploading_progress: '上传中 ({current}/{total})...',
    upload_failed: '上传失败 ({name}): {error}',
    nav_dot_title: '跳转到步骤 {n}',
    select_at_least_one: '请至少选择一个句子',
    group_count_suffix: ' 句',
    detecting: '识别中...',
    detect_failed: '识别失败: ',
    select_category_first: '请先选择至少一个分类',
    matching: '匹配中...',
    match_failed: '匹配失败: ',
    build_failed: '构建失败: ',
    burning_subtitle: '正在烧录字幕...',
    outputting_video: '正在输出视频...',
    mod1_title: '视频剪辑',
    mod1_desc: '上传 - 转录 - 勾选 - 排序 - 输出',
    mod2_title: 'AI混剪',
    mod2_desc: '脚本 - AI画面 - 视频生成 - 混剪输出',
    remix_subtitle: '脚本 - AI画面 - Seedance视频 - 混剪',
    remix_create_lib: '创建素材库',
    remix_verify: '验证并继续',
    remix_next_script: '下一步：编写脚本',
    remix_translate: '翻译为印尼语',
    remix_compliance: '合规审核',
    remix_next_frames: '下一步：AI画面',
    remix_upload_hint: '上传实物素材（至少2个，每个8秒）',
    remix_invest_video: '招商视频',
    remix_invest_desc: '40秒：16秒AI + 16秒实拍 + 8秒CTA',
    remix_s0_title: '素材库初始化',
    remix_s1_title: '选择视频类型',
    remix_s2_title: '脚本编辑',
    remix_s3_title: 'AI首尾帧',
    remix_s4_title: 'Seedance 视频生成',
    remix_s5_title: '最终拼接',
    remix_gen_frames: '生成首尾帧',
    remix_next_videos: '下一步：生成视频',
    remix_next_assembly: '下一步：拼接',
    remix_assemble: '拼接最终视频',
    remix_assembly_desc: '16秒AI + 16秒实物素材配画外音 + 8秒CTA = 40秒',
    remix_gen_videos: '生成视频',
    remix_resolution_label: '分辨率：',
    btn_back: '返回',
  },
  id: {
    subtitle: 'Unggah klip wawancara → Transkripsi & terjemahan → Pilih & urutkan → Edit otomatis',
    step1_title: 'Unggah Klip Video',
    upload_hint: 'Seret file video ke sini, atau klik untuk memilih',
    upload_formats: 'Mendukung mp4 / mov / webm, bisa ditambah berkali-kali',
    audio_lang: 'Bahasa Audio',
    lang_id: 'Indonesia (Indonesian)',
    lang_ko: 'Korea (Korean)',
    lang_ja: 'Jepang (Japanese)',
    lang_zh: 'Mandarin (Chinese)',
    lang_auto: 'Deteksi Otomatis',
    vocab_label: 'Kata Khusus (Opsional)',
    vocab_placeholder: 'Nama merek, nama orang, dll., pisahkan dengan koma. Contoh: Veirfoo, PDRN, Tulandut',
    vocab_hint: 'Membantu Gemini mengenali kata-kata yang jarang digunakan',
    btn_upload: 'Unggah & Mulai Transkripsi',
    step2_title: 'Transkripsi + Terjemahan',
    status_preparing: 'Mempersiapkan...',
    step3_title: 'Pilih Kalimat yang Diperlukan',
    btn_select_all: 'Pilih Semua',
    btn_select_none: 'Hapus Semua',
    btn_back_upload: 'Kembali ke Unggah',
    btn_next_sort: 'Lanjut: Urutkan',
    step4_title: 'Seret untuk Mengatur Urutan',
    sort_hint: 'Seret judul klip untuk mengatur urutan grup, seret kalimat untuk memindahkan dalam/antar grup',
    btn_back_select: 'Kembali ke Pilihan',
    btn_next_keywords: 'Lanjut: Kata Kunci',
    step5_title: 'Sorotan Kata Kunci',
    keyword_desc: 'Pilih kategori otomatis atau masukkan kata kunci manual. Kata yang disorot akan diperbesar + kuning di subtitle.',
    chip_numbers: 'Angka',
    chip_money: 'Nominal',
    chip_time: 'Waktu',
    chip_age: 'Usia',
    chip_brand: 'Merek',
    chip_emotion: 'Penekanan',
    btn_auto_detect: 'Deteksi Otomatis',
    manual_keyword_label: 'Atau masukkan kata kunci secara manual:',
    keyword_placeholder: 'Contoh: benar, juta, sehari',
    btn_match_keywords: 'Cocokkan Kata Kunci',
    btn_back_sort: 'Kembali ke Urutan',
    btn_build_video: 'Buat Video',
    step6_title: 'Buat Video',
    btn_back_keywords: 'Kembali ke Kata Kunci',
    stage_trimming: 'Potong Klip',
    stage_concat: 'Gabung Video',
    stage_subtitle: 'Buat Subtitle',
    stage_burning: 'Tanam Subtitle',
    stage_compressing: 'Kompres Output',
    status_building: 'Memproses...',
    subtitle_choice_prompt: 'Penggabungan selesai! Apakah perlu menambahkan subtitle otomatis?',
    btn_add_subtitle: 'Tambah Subtitle',
    btn_download_no_subtitle: 'Unduh Langsung (Tanpa Subtitle)',
    download_complete: 'Video berhasil dibuat!',
    btn_download_video: 'Unduh Video',
    violation_title: 'Pemeriksaan Kata Terlarang',
    violation_summary_clean: 'Tidak ada kata terlarang terdeteksi',
    violation_summary_found: 'Terdeteksi {count} kata terlarang ({sentences} kalimat terkait)',
    violation_recheck: 'Periksa Ulang',
    violation_cat_absolute: 'Klaim Absolut',
    violation_cat_medical: 'Klaim Medis',
    violation_cat_beauty: 'Red Line Kecantikan',
    violation_cat_exaggerated: 'Klaim Berlebihan',
    violation_cat_weight: 'Klaim Diet',
    violation_cat_competitor: 'Sebutan Kompetitor',
    violation_cat_external: 'Pengalihan Eksternal',
    violation_cat_promo: 'Promosi Terlarang',
    violation_rule_absolute: 'Dilarang menggunakan klaim absolut (Kebijakan E-commerce/Iklan TikTok)',
    violation_rule_medical: 'Kosmetik tidak boleh membuat klaim medis (Red Line TikTok)',
    violation_rule_beauty: 'Dilarang menjanjikan pengobatan masalah kulit (Kebijakan Iklan+E-commerce TikTok)',
    violation_rule_exaggerated: 'Dilarang menggunakan klaim berlebihan (Kebijakan E-commerce/Livestream TikTok)',
    violation_rule_weight: 'Dilarang membuat klaim diet (Kebijakan Iklan TikTok)',
    violation_rule_competitor: 'Dilarang menyebut platform kompetitor di livestream/iklan (Kebijakan E-commerce TikTok)',
    violation_rule_external: 'Dilarang mengalihkan ke platform eksternal (Kebijakan E-commerce TikTok)',
    violation_rule_promo: 'Dilarang menggunakan kata promosi yang menciptakan urgensi (Kebijakan E-commerce TikTok)',
    uploading_progress: 'Mengunggah ({current}/{total})...',
    upload_failed: 'Gagal mengunggah ({name}): {error}',
    nav_dot_title: 'Lompat ke langkah {n}',
    select_at_least_one: 'Pilih minimal satu kalimat',
    group_count_suffix: ' kalimat',
    detecting: 'Mendeteksi...',
    detect_failed: 'Gagal mendeteksi: ',
    select_category_first: 'Pilih minimal satu kategori terlebih dahulu',
    matching: 'Mencocokkan...',
    match_failed: 'Gagal mencocokkan: ',
    build_failed: 'Gagal memproses: ',
    burning_subtitle: 'Sedang menanamkan subtitle...',
    outputting_video: 'Sedang mengekspor video...',
    mod1_title: 'Video Clip Assembler',
    mod1_desc: 'Unggah - Transkripsi - Pilih - Urutkan - Buat',
    mod2_title: 'AI Remix',
    mod2_desc: 'Skrip - AI Frame - Video Gen - Assembly',
    remix_subtitle: 'Skrip - AI Frame - Seedance Video - Assembly',
    remix_create_lib: 'Buat Perpustakaan Aset',
    remix_verify: 'Verifikasi & Lanjutkan',
    remix_next_script: 'Lanjut: Tulis Naskah',
    remix_translate: 'Terjemahkan ke Indonesia',
    remix_compliance: 'Periksa Kepatuhan',
    remix_next_frames: 'Lanjut: AI Frame',
    remix_upload_hint: 'Unggah klip real footage (min 2, 8 detik)',
    remix_invest_video: 'Video Investasi',
    remix_invest_desc: '40d: 16d AI + 16d Real + 8d CTA',
    remix_s0_title: 'Inisialisasi Perpustakaan Aset',
    remix_s1_title: 'Pilih Jenis Video',
    remix_s2_title: 'Editor Naskah',
    remix_s3_title: 'AI Frame Awal/Akhir',
    remix_s4_title: 'Pembuatan Video Seedance',
    remix_s5_title: 'Perakitan Akhir',
    remix_gen_frames: 'Buat Frame',
    remix_next_videos: 'Lanjut: Buat Video',
    remix_next_assembly: 'Lanjut: Perakitan',
    remix_assemble: 'Rakit Video Akhir',
    remix_assembly_desc: '16d AI + 16d footage + suara latar + 8d CTA = 40d',
    remix_gen_videos: 'Buat Video',
    remix_resolution_label: 'Resolusi:',
    btn_back: 'Kembali',
  },
  en: {
    subtitle: 'Upload interview clips → Transcribe & translate → Select & sort → Auto-edit',
    step1_title: 'Upload Video Clips',
    upload_hint: 'Drag & drop video files here, or click to select',
    upload_formats: 'Supports mp4 / mov / webm, can add multiple times',
    audio_lang: 'Audio Language',
    lang_id: 'Indonesian',
    lang_ko: 'Korean',
    lang_ja: 'Japanese',
    lang_zh: 'Chinese',
    lang_auto: 'Auto Detect',
    vocab_label: 'Custom Vocabulary (Optional)',
    vocab_placeholder: 'Brand names, proper nouns, etc., comma-separated. e.g.: Veirfoo, PDRN, Tulandut',
    vocab_hint: 'Helps Gemini accurately recognize uncommon words',
    btn_upload: 'Upload & Start Transcription',
    step2_title: 'Transcribe + Translate',
    status_preparing: 'Preparing...',
    step3_title: 'Select Sentences',
    btn_select_all: 'Select All',
    btn_select_none: 'Deselect All',
    btn_back_upload: 'Back to Upload',
    btn_next_sort: 'Next: Sort',
    step4_title: 'Drag to Reorder',
    sort_hint: 'Drag clip titles to reorder groups, drag sentences to move within or across groups',
    btn_back_select: 'Back to Selection',
    btn_next_keywords: 'Next: Keywords',
    step5_title: 'Keyword Highlights',
    keyword_desc: 'Choose auto-categories or enter keywords manually. Highlighted words appear enlarged + yellow in subtitles.',
    chip_numbers: 'Numbers',
    chip_money: 'Amounts',
    chip_time: 'Time',
    chip_age: 'Age',
    chip_brand: 'Brands',
    chip_emotion: 'Emphasis',
    btn_auto_detect: 'Auto Detect Categories',
    manual_keyword_label: 'Or enter keywords manually:',
    keyword_placeholder: 'e.g.: really, million, one day',
    btn_match_keywords: 'Match Keywords',
    btn_back_sort: 'Back to Sort',
    btn_build_video: 'Build Video',
    step6_title: 'Build Video',
    btn_back_keywords: 'Back to Keywords',
    stage_trimming: 'Trimming Clips',
    stage_concat: 'Concatenating Video',
    stage_subtitle: 'Generating Subtitles',
    stage_burning: 'Burning Subtitles',
    stage_compressing: 'Compressing Output',
    status_building: 'Building...',
    subtitle_choice_prompt: 'Concatenation complete! Would you like to burn subtitles automatically?',
    btn_add_subtitle: 'Add Subtitles',
    btn_download_no_subtitle: 'Download Directly (No Subtitles)',
    download_complete: 'Video generated successfully!',
    btn_download_video: 'Download Video',
    violation_title: 'Banned Words Check',
    violation_summary_clean: 'No banned words detected',
    violation_summary_found: 'Detected {count} banned words ({sentences} sentences affected)',
    violation_recheck: 'Re-check',
    violation_cat_absolute: 'Absolute Claims',
    violation_cat_medical: 'Medical Claims',
    violation_cat_beauty: 'Beauty Red Lines',
    violation_cat_exaggerated: 'Exaggerated Claims',
    violation_cat_weight: 'Weight Loss Claims',
    violation_cat_competitor: 'Competitor Mention',
    violation_cat_external: 'External Routing',
    violation_cat_promo: 'Promo Violation',
    violation_rule_absolute: 'Absolute claims prohibited (TikTok E-commerce/Ad Policy)',
    violation_rule_medical: 'Cosmetics cannot make medical claims (TikTok Red Line)',
    violation_rule_beauty: 'Cannot promise skin problem treatment/removal (TikTok Ad+E-commerce Policy)',
    violation_rule_exaggerated: 'Exaggerated claims prohibited (TikTok E-commerce/Livestream Policy)',
    violation_rule_weight: 'Weight loss claims prohibited (TikTok Ad Policy)',
    violation_rule_competitor: 'Competitor platform mentions banned in livestream/ads (TikTok E-commerce Policy)',
    violation_rule_external: 'External platform routing banned (TikTok E-commerce Policy)',
    violation_rule_promo: 'Urgency-creating promo language banned (TikTok E-commerce Policy)',
    uploading_progress: 'Uploading ({current}/{total})...',
    upload_failed: 'Upload failed ({name}): {error}',
    nav_dot_title: 'Jump to step {n}',
    select_at_least_one: 'Please select at least one sentence',
    group_count_suffix: ' sentences',
    detecting: 'Detecting...',
    detect_failed: 'Detection failed: ',
    select_category_first: 'Please select at least one category first',
    matching: 'Matching...',
    match_failed: 'Matching failed: ',
    build_failed: 'Build failed: ',
    burning_subtitle: 'Burning subtitles...',
    outputting_video: 'Exporting video...',
    mod1_title: 'Video Clip Assembler',
    mod1_desc: 'Upload - Transcribe - Select - Sort - Build',
    mod2_title: 'AI Remix',
    mod2_desc: 'Script - AI Frames - Video Gen - Assembly',
    remix_subtitle: 'Script - AI Frames - Seedance Video - Assembly',
    remix_create_lib: 'Create Asset Library',
    remix_verify: 'Verify & Continue',
    remix_next_script: 'Next: Write Script',
    remix_translate: 'Translate to Indonesian',
    remix_compliance: 'Check Compliance',
    remix_next_frames: 'Next: AI Frames',
    remix_upload_hint: 'Upload real footage clips (min 2, 8s each)',
    remix_invest_video: 'Investment Video',
    remix_invest_desc: '40s: 16s AI + 16s Real + 8s CTA',
    remix_s0_title: 'Asset Library Setup',
    remix_s1_title: 'Select Video Type',
    remix_s2_title: 'Script Editor',
    remix_s3_title: 'AI First/Last Frames',
    remix_s4_title: 'Seedance Video Generation',
    remix_s5_title: 'Final Assembly',
    remix_gen_frames: 'Generate Frames',
    remix_next_videos: 'Next: Generate Videos',
    remix_next_assembly: 'Next: Assembly',
    remix_assemble: 'Assemble Final Video',
    remix_assembly_desc: '16s AI + 16s real footage with voiceover + 8s CTA = 40s',
    remix_gen_videos: 'Generate Videos',
    remix_resolution_label: 'Resolution:',
    btn_back: 'Back',
  },
};

let currentLang = 'zh';

function switchLang(lang) {
  currentLang = lang;
  localStorage.setItem('vca_ui_lang', lang);

  const dict = I18N[lang] || I18N.zh;

  // Update all elements with data-i18n attribute
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key] !== undefined) {
      el.textContent = dict[key];
    }
  });

  // Update all elements with data-i18n-placeholder attribute
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (dict[key] !== undefined) {
      el.placeholder = dict[key];
    }
  });

  // Update the language switcher selection
  const uiLangSelect = document.getElementById('uiLang');
  if (uiLangSelect) uiLangSelect.value = lang;
}

// Helper to get a translated string by key (for dynamic JS usage)
function t(key, replacements) {
  const dict = I18N[currentLang] || I18N.zh;
  let str = dict[key] || I18N.zh[key] || key;
  if (replacements) {
    for (const [k, v] of Object.entries(replacements)) {
      str = str.replace('{' + k + '}', v);
    }
  }
  return str;
}

// === State ===
let currentStep = 1;
let maxStepReached = 1;
let uploadedFiles = [];  // {id, filename}
let clipsData = {};      // from /api/clips
let selectedSentences = []; // after checkbox selection
let sortedGroups = [];      // [{clipId, filename, sentences: [...]}]
let keywordMap = {};     // {indo_word: true}
let autoKeywordMap = {}; // from category detection

const TOTAL_STEPS = 6;

// === Init ===
document.addEventListener('DOMContentLoaded', () => {
  // Restore saved language preference
  const savedLang = localStorage.getItem('vca_ui_lang');
  if (savedLang && I18N[savedLang]) {
    switchLang(savedLang);
  }
  renderNavDots();
  setupUpload();
});

// === Navigation ===
function goToStep(n) {
  currentStep = n;
  if (n > maxStepReached) maxStepReached = n;
  for (let i = 1; i <= TOTAL_STEPS; i++) {
    const el = document.getElementById(`step${i}`);
    if (el) el.classList.toggle('active', i === n);
  }
  renderNavDots();
}

function renderNavDots() {
  const container = document.getElementById('navDots');
  container.innerHTML = '';
  for (let i = 1; i <= TOTAL_STEPS; i++) {
    const dot = document.createElement('div');
    dot.className = 'nav-dot';
    if (i === currentStep) dot.classList.add('active');
    if (i < currentStep) dot.classList.add('done');
    if (i !== currentStep && i <= maxStepReached) {
      dot.style.cursor = 'pointer';
      dot.title = t('nav_dot_title', { n: i });
      dot.addEventListener('click', () => goToStep(i));
    }
    container.appendChild(dot);
  }
}

// === Step 1: Upload ===
let pendingFiles = [];

function setupUpload() {
  const area = document.getElementById('uploadArea');
  const btn = document.getElementById('btnUpload');

  area.addEventListener('click', () => {
    // Create a fresh input each time to guarantee change event fires
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = 'video/*';
    input.style.display = 'none';
    input.addEventListener('change', () => {
      handleFiles(input.files);
      input.remove();
    });
    document.body.appendChild(input);
    input.click();
  });

  area.addEventListener('dragover', (e) => {
    e.preventDefault();
    area.classList.add('dragover');
  });

  area.addEventListener('dragleave', () => {
    area.classList.remove('dragover');
  });

  area.addEventListener('drop', (e) => {
    e.preventDefault();
    area.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
  });

  btn.addEventListener('click', startUploadAndTranscribe);
}

function handleFiles(fileList) {
  const newFiles = Array.from(fileList).filter(f =>
    f.type.startsWith('video/') || f.name.match(/\.(mp4|mov|webm|avi|mkv)$/i)
  );

  // Append new files (skip duplicates by name+size)
  for (const nf of newFiles) {
    const dup = pendingFiles.some(pf => pf.name === nf.name && pf.size === nf.size);
    if (!dup) pendingFiles.push(nf);
  }

  renderPendingFiles();
  document.getElementById('btnUpload').disabled = pendingFiles.length === 0;
}

function renderPendingFiles() {
  const list = document.getElementById('fileList');
  list.innerHTML = '';

  pendingFiles.forEach((f, i) => {
    const div = document.createElement('div');
    div.className = 'file-item';
    const sizeMB = (f.size / 1024 / 1024).toFixed(1);
    div.innerHTML = `
      <span class="name">${escapeHtml(f.name)}</span>
      <span class="size">${sizeMB} MB</span>
      <span class="remove-btn" onclick="removeFile(${i})" style="cursor:pointer;color:#f66;margin-left:8px;">&#x2715;</span>
    `;
    list.appendChild(div);
  });
}

function removeFile(index) {
  pendingFiles.splice(index, 1);
  renderPendingFiles();
  document.getElementById('btnUpload').disabled = pendingFiles.length === 0;
}

async function startUploadAndTranscribe() {
  const btn = document.getElementById('btnUpload');
  btn.disabled = true;

  // Send language + vocabulary
  const langSelect = document.getElementById('langSelect');
  const language = langSelect ? langSelect.value : 'id';
  const vocabInput = document.getElementById('vocabInput');
  const vocab = vocabInput && vocabInput.value.trim()
    ? vocabInput.value.split(/[,，]/).map(v => v.trim()).filter(Boolean)
    : [];
  try {
    var vResp = await fetch('/api/vocabulary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vocabulary: vocab, language }),
    });
    if (!vResp.ok) throw new Error('HTTP ' + vResp.status);
  } catch (e) {
    btn.disabled = false;
    btn.textContent = t('upload_and_transcribe');
    return;
  }

  const total = pendingFiles.length;
  uploadedFiles = [];

  // Clear server state
  try {
    var cResp = await fetch('/api/clear', { method: 'POST' });
    if (!cResp.ok) throw new Error('HTTP ' + cResp.status);
  } catch (e) {
    btn.disabled = false;
    btn.textContent = t('upload_and_transcribe');
    return;
  }

  // Upload files one by one
  for (let i = 0; i < total; i++) {
    const f = pendingFiles[i];
    btn.textContent = t('uploading_progress', { current: i + 1, total: total });
    updateFileListProgress(i, total);

    try {
      const resp = await fetch('/api/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/octet-stream',
          'X-Filename': encodeURIComponent(f.name),
        },
        body: f,
      });
      if (!resp.ok) throw new Error('Upload HTTP ' + resp.status);
      const data = await resp.json();
      if (data.error) throw new Error(data.error);
      uploadedFiles.push(data);
    } catch (err) {
      alert(t('upload_failed', { name: f.name, error: err.message }));
      btn.disabled = false;
      btn.textContent = t('btn_upload');
      return;
    }
  }

  // All uploaded — show check marks
  const list = document.getElementById('fileList');
  list.innerHTML = '';
  uploadedFiles.forEach(f => {
    const div = document.createElement('div');
    div.className = 'file-item';
    div.innerHTML = `
      <span class="check">&#x2713;</span>
      <span class="name">${decodeURIComponent(f.filename)}</span>
    `;
    list.appendChild(div);
  });

  // Start transcription
  goToStep(2);
  await startTranscription();
}

function updateFileListProgress(currentIdx, total) {
  const list = document.getElementById('fileList');
  list.innerHTML = '';
  pendingFiles.forEach((f, i) => {
    const div = document.createElement('div');
    div.className = 'file-item';
    const sizeMB = (f.size / 1024 / 1024).toFixed(1);
    let status = '';
    if (i < currentIdx) status = '<span class="check">&#x2713;</span>';
    else if (i === currentIdx) status = '<span class="uploading">&#x25B6;</span>';
    else status = '<span class="pending">&#x25CB;</span>';
    div.innerHTML = `
      ${status}
      <span class="name">${f.name}</span>
      <span class="size">${sizeMB} MB</span>
    `;
    list.appendChild(div);
  });
}

let _pollStatusInterval = null;

async function startTranscription() {
  const btn = document.getElementById('btnUpload');
  if (btn) btn.disabled = true;
  try {
    var tResp = await fetch('/api/transcribe', { method: 'POST' });
    if (!tResp.ok) {
      var tData = await tResp.json().catch(function() { return {}; });
      alert(tData.error || 'Transcription failed (HTTP ' + tResp.status + ')');
      if (btn) btn.disabled = false;
      return;
    }
  } catch (e) {
    if (btn) btn.disabled = false;
    return;
  }
  pollStatus();
}

function pollStatus() {
  if (_pollStatusInterval) clearInterval(_pollStatusInterval);
  _pollStatusInterval = setInterval(async () => {
    try {
      const resp = await fetch('/api/status');
      const data = await resp.json();

      document.getElementById('progressFill').style.width = data.progress + '%';
      document.getElementById('statusText').textContent = data.message;

      if (data.status === 'done') {
        clearInterval(_pollStatusInterval);
        _pollStatusInterval = null;
        await loadClips();
        renderSentences();
        goToStep(3);
      } else if (data.status === 'error') {
        clearInterval(_pollStatusInterval);
        _pollStatusInterval = null;
        document.getElementById('statusText').textContent = data.message;
      }
    } catch (e) {
      // ignore polling errors
    }
  }, 1000);
}

async function loadClips() {
  try {
    const resp = await fetch('/api/clips');
    clipsData = await resp.json();
  } catch (e) {
    console.error('Failed to load clips:', e);
  }
}

// === Step 3: Select sentences + Violation Check ===
function renderSentences() {
  const container = document.getElementById('sentenceList');
  container.innerHTML = '';

  for (const [clipId, clip] of Object.entries(clipsData)) {
    const group = document.createElement('div');
    group.className = 'clip-group';

    const header = document.createElement('div');
    header.className = 'clip-group-header';
    header.textContent = clip.filename;
    group.appendChild(header);

    clip.sentences.forEach((s, idx) => {
      const item = document.createElement('div');
      item.className = 'sentence-item';

      const startStr = formatTime(s.start);
      const endStr = formatTime(s.end);

      // Scan both original text and translation for violations
      const textViolations = scanBannedWords(s.text);
      const cnViolations = scanBannedWords(s.translation || '');
      const hasViolation = textViolations.length > 0 || cnViolations.length > 0;

      item.innerHTML = `
        <input type="checkbox" data-clip-id="${clipId}" data-idx="${idx}" checked>
        <div class="sentence-content">
          <div class="sentence-time">${startStr} - ${endStr}</div>
          ${hasViolation ? `<div class="sentence-violations-preview">${highlightBannedWords(s.text, textViolations)}</div>` : ''}
          <input type="text" class="sentence-edit${hasViolation ? ' has-violation' : ''}" data-clip-id="${clipId}" data-idx="${idx}" data-field="text" value="${escapeHtml(s.text)}">
          ${cnViolations.length > 0 ? `<div class="sentence-violations-preview cn">${highlightBannedWords(s.translation || '', cnViolations)}</div>` : ''}
          <input type="text" class="sentence-edit sentence-edit-cn${cnViolations.length > 0 ? ' has-violation' : ''}" data-clip-id="${clipId}" data-idx="${idx}" data-field="translation" value="${escapeHtml(s.translation || '')}">
          ${hasViolation ? renderViolationTags(textViolations, cnViolations) : ''}
        </div>
      `;
      group.appendChild(item);
    });

    container.appendChild(group);
  }

  // Sync edits back to clipsData + re-check violations on edit
  container.querySelectorAll('.sentence-edit').forEach(input => {
    input.addEventListener('change', () => {
      const clip = clipsData[input.dataset.clipId];
      if (clip && clip.sentences[input.dataset.idx]) {
        clip.sentences[input.dataset.idx][input.dataset.field] = input.value;
      }
    });
  });

  // Update violation summary
  updateViolationSummary();
}

/** Render violation category tags below a sentence */
function renderViolationTags(textViolations, cnViolations) {
  const allViolations = [...textViolations, ...cnViolations];
  const catMap = {};
  for (const v of allViolations) {
    if (!catMap[v.cat]) catMap[v.cat] = [];
    if (!catMap[v.cat].includes(v.word)) catMap[v.cat].push(v.word);
  }

  let html = '<div class="violation-tags">';
  for (const [cat, words] of Object.entries(catMap)) {
    const info = BANNED_CATEGORIES[cat];
    const label = info ? (info[currentLang] || info.zh) : cat;
    const rule = t('violation_rule_' + cat);
    html += `<span class="violation-tag" style="--tag-color:${info ? info.color : '#e74c3c'}" title="${escapeHtml(rule)}">${label}: ${words.map(escapeHtml).join(', ')}</span>`;
  }
  html += '</div>';
  return html;
}

/** Update the violation summary panel */
function updateViolationSummary() {
  const panel = document.getElementById('violationSummary');
  if (!panel) return;

  let totalViolations = 0;
  let sentencesWithViolations = 0;

  for (const clip of Object.values(clipsData)) {
    for (const s of (clip.sentences || [])) {
      const tv = scanBannedWords(s.text);
      const cv = scanBannedWords(s.translation || '');
      const count = tv.length + cv.length;
      if (count > 0) {
        totalViolations += count;
        sentencesWithViolations++;
      }
    }
  }

  if (totalViolations === 0) {
    panel.className = 'violation-summary clean';
    panel.innerHTML = `<span class="violation-icon">&#x2705;</span> <span>${t('violation_summary_clean')}</span>`;
  } else {
    panel.className = 'violation-summary warning';
    panel.innerHTML = `<span class="violation-icon">&#x26A0;&#xFE0F;</span> <span>${t('violation_summary_found', { count: totalViolations, sentences: sentencesWithViolations })}</span>
      <button class="btn btn-secondary btn-sm" onclick="recheckViolations()">${t('violation_recheck')}</button>`;
  }
}

/** Re-check violations after user edits */
function recheckViolations() {
  // Re-sync edits from DOM to clipsData
  document.querySelectorAll('#sentenceList .sentence-edit').forEach(input => {
    const clip = clipsData[input.dataset.clipId];
    if (clip && clip.sentences[input.dataset.idx]) {
      clip.sentences[input.dataset.idx][input.dataset.field] = input.value;
    }
  });
  // Re-render
  renderSentences();
}

function selectAll() {
  document.querySelectorAll('#sentenceList input[type="checkbox"]').forEach(cb => cb.checked = true);
}

function selectNone() {
  document.querySelectorAll('#sentenceList input[type="checkbox"]').forEach(cb => cb.checked = false);
}

// === Step 4: Group Sort ===
function goToSort() {
  // Gather selected sentences grouped by clip
  const grouped = {};

  document.querySelectorAll('#sentenceList input[type="checkbox"]:checked').forEach(cb => {
    const clipId = cb.dataset.clipId;
    const idx = parseInt(cb.dataset.idx);
    const clip = clipsData[clipId];
    if (clip && clip.sentences[idx]) {
      if (!grouped[clipId]) {
        grouped[clipId] = {
          clipId,
          filename: clip.filename,
          sentences: [],
        };
      }
      const s = clip.sentences[idx];
      grouped[clipId].sentences.push({
        ...s,
        clip_id: clipId,
        clip_filename: clip.filename,
      });
    }
  });

  sortedGroups = Object.values(grouped);

  if (sortedGroups.reduce((n, g) => n + g.sentences.length, 0) === 0) {
    alert(t('select_at_least_one'));
    return;
  }

  renderSortGroups();
  goToStep(4);
}

function renderSortGroups() {
  const container = document.getElementById('sortGroups');
  container.innerHTML = '';

  sortedGroups.forEach((group, gi) => {
    const groupEl = document.createElement('div');
    groupEl.className = 'sort-group';
    groupEl.dataset.groupIndex = gi;

    // Group header (draggable at group level)
    const header = document.createElement('div');
    header.className = 'sort-group-header';
    header.innerHTML = `
      <span class="sort-handle group-handle">&#x2630;</span>
      <span class="group-name">${escapeHtml(group.filename)}</span>
      <span class="group-count">${group.sentences.length}${t('group_count_suffix')}</span>
    `;
    groupEl.appendChild(header);

    // Sentences within group
    const sentList = document.createElement('ul');
    sentList.className = 'sort-group-sentences';
    sentList.dataset.groupIndex = gi;

    group.sentences.forEach((s, si) => {
      const li = document.createElement('li');
      li.className = 'sort-item';
      li.dataset.groupIndex = gi;
      li.dataset.sentIndex = si;
      li.innerHTML = `
        <span class="sort-handle">&#x2630;</span>
        <div class="sentence-content">
          <div class="sentence-indo">${escapeHtml(s.text)}</div>
          <div class="sentence-cn">${escapeHtml(s.translation || '')}</div>
        </div>
      `;
      sentList.appendChild(li);
    });

    groupEl.appendChild(sentList);
    container.appendChild(groupEl);

    // Inner sortable (sentences within group)
    if (window.Sortable) {
      Sortable.create(sentList, {
        animation: 150,
        handle: '.sort-handle',
        group: 'sentences',
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        onEnd: syncSortState,
      });
    }
  });

  // Outer sortable (groups)
  if (window.Sortable) {
    Sortable.create(container, {
      animation: 200,
      handle: '.group-handle',
      ghostClass: 'sortable-ghost',
      chosenClass: 'sortable-chosen',
      onEnd: syncGroupOrder,
    });
  }
}

function syncGroupOrder() {
  // Re-read group order from DOM
  const container = document.getElementById('sortGroups');
  const newGroups = [];
  container.querySelectorAll('.sort-group').forEach(groupEl => {
    const gi = parseInt(groupEl.dataset.groupIndex);
    newGroups.push(sortedGroups[gi]);
  });
  sortedGroups = newGroups;
  // Re-render with updated indices
  renderSortGroups();
}

function syncSortState() {
  // Re-read sentence order from DOM for each group
  const container = document.getElementById('sortGroups');
  container.querySelectorAll('.sort-group').forEach((groupEl, newGi) => {
    const origGi = parseInt(groupEl.dataset.groupIndex);
    const newSentences = [];
    groupEl.querySelectorAll('.sort-item').forEach(li => {
      const ogi = parseInt(li.dataset.groupIndex);
      const osi = parseInt(li.dataset.sentIndex);
      newSentences.push(sortedGroups[ogi].sentences[osi]);
    });
    sortedGroups[origGi].sentences = newSentences;
  });
}

// Get flat sorted sentences for build
function getFlatSortedSentences() {
  // Re-sync from DOM first
  syncSortState();
  const flat = [];
  const container = document.getElementById('sortGroups');
  container.querySelectorAll('.sort-group').forEach(groupEl => {
    const gi = parseInt(groupEl.dataset.groupIndex);
    sortedGroups[gi].sentences.forEach(s => flat.push(s));
  });
  return flat;
}

// === Step 5: Keywords ===
function goToKeywords() {
  goToStep(5);
}

function toggleChip(el) {
  el.classList.toggle('active');
}

async function autoKeywords() {
  const chips = document.querySelectorAll('#categoryChips .chip.active');
  const categories = Array.from(chips).map(c => c.dataset.cat);

  if (categories.length === 0) {
    alert(t('select_category_first'));
    return;
  }

  const btn = document.getElementById('btnAutoKw');
  btn.disabled = true;
  btn.textContent = t('detecting');

  try {
    const resp = await fetch('/api/keyword-categories', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ categories }),
    });
    const data = await resp.json();
    if (!resp.ok || data.error) throw new Error(data.error || 'HTTP ' + resp.status);
    autoKeywordMap = data.matches || {};
    renderAutoKeywords(autoKeywordMap);
  } catch (err) {
    alert(t('detect_failed') + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = t('btn_auto_detect');
  }
}

function renderAutoKeywords(matches) {
  const container = document.getElementById('keywordAutoResults');
  container.innerHTML = '';

  const catLabels = {
    numbers: t('chip_numbers'), money: t('chip_money'), time: t('chip_time'),
    age: t('chip_age'), brand: t('chip_brand'), emotion: t('chip_emotion'),
  };

  for (const [word, cat] of Object.entries(matches)) {
    const div = document.createElement('div');
    div.className = 'auto-keyword-item';
    div.innerHTML = `
      <input type="checkbox" data-word="${escapeHtml(word)}" checked>
      <span class="auto-kw-word">${escapeHtml(word)}</span>
      <span class="auto-kw-cat">${catLabels[cat] || cat}</span>
    `;
    container.appendChild(div);
  }
}

async function matchKeywords() {
  const input = document.getElementById('keywordInput').value.trim();
  if (!input) return;

  const keywords = input.split(/[,，]/).map(k => k.trim()).filter(Boolean);
  const btn = document.getElementById('btnMatchKw');
  btn.disabled = true;
  btn.textContent = t('matching');

  try {
    const resp = await fetch('/api/keywords', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keywords }),
    });
    const data = await resp.json();
    if (!resp.ok || data.error) throw new Error(data.error || 'HTTP ' + resp.status);
    renderKeywordMatches(data.matches || {});
  } catch (err) {
    alert(t('match_failed') + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = t('btn_match_keywords');
  }
}

function renderKeywordMatches(matches) {
  const container = document.getElementById('keywordMatches');
  container.innerHTML = '';

  for (const [cn, indo] of Object.entries(matches)) {
    const div = document.createElement('div');
    div.className = 'keyword-match';
    div.innerHTML = `
      <span class="cn">${escapeHtml(cn)}</span>
      <span class="arrow">&#x2192;</span>
      <input type="text" value="${escapeHtml(indo || '')}" data-cn="${escapeHtml(cn)}">
    `;
    container.appendChild(div);
  }
}

function getKeywordHighlights() {
  const highlights = {};

  // From auto-detected categories
  document.querySelectorAll('#keywordAutoResults input[type="checkbox"]:checked').forEach(cb => {
    const word = cb.dataset.word;
    if (word) highlights[word] = true;
  });

  // From manual keyword matches
  document.querySelectorAll('#keywordMatches input').forEach(input => {
    const val = input.value.trim();
    if (val) highlights[val] = true;
  });

  return highlights;
}

// === Step 6: Build ===
const STAGE_ORDER = ['trimming', 'concat', 'subtitle', 'burning', 'compressing'];

let _buildInProgress = false;

async function buildVideo() {
  if (_buildInProgress) return;
  _buildInProgress = true;

  // Hide back button once building starts
  const backBtn = document.getElementById('step6Back');
  if (backBtn) backBtn.style.display = 'none';

  keywordMap = getKeywordHighlights();

  const sentences = getFlatSortedSentences();
  const selections = sentences.map(s => ({
    clip_path: s.clip_path,
    start: s.start,
    end: s.end,
    text: s.text,
    words: s.words || [],
  }));

  goToStep(6);
  resetBuildStages();

  try {
    var bResp = await fetch('/api/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        selections,
        keywords: keywordMap,
      }),
    });
    var bData = await bResp.json().catch(function() { return {}; });
    if (!bResp.ok || bData.error) {
      _buildInProgress = false;
      document.getElementById('buildStatusText').textContent = bData.error || 'Build failed (HTTP ' + bResp.status + ')';
      return;
    }
    pollBuild();
  } catch (err) {
    _buildInProgress = false;
    document.getElementById('buildStatusText').textContent = t('build_failed') + err.message;
  }
}

function resetBuildStages() {
  document.querySelectorAll('.build-stage').forEach(el => {
    el.classList.remove('active', 'done');
    el.querySelector('.stage-icon').innerHTML = '&#x25CB;';
  });
}

function updateBuildStages(currentStage) {
  const stages = document.querySelectorAll('.build-stage');
  let reachedCurrent = false;

  stages.forEach(el => {
    const stage = el.dataset.stage;
    if (stage === currentStage) {
      reachedCurrent = true;
      el.classList.add('active');
      el.classList.remove('done');
      el.querySelector('.stage-icon').innerHTML = '&#x25B6;';
    } else if (!reachedCurrent) {
      el.classList.remove('active');
      el.classList.add('done');
      el.querySelector('.stage-icon').innerHTML = '&#x2713;';
    } else {
      el.classList.remove('active', 'done');
      el.querySelector('.stage-icon').innerHTML = '&#x25CB;';
    }
  });
}

let _pollBuildInterval = null;

function pollBuild() {
  if (_pollBuildInterval) clearInterval(_pollBuildInterval);
  _pollBuildInterval = setInterval(async () => {
    try {
      const resp = await fetch('/api/status');
      const data = await resp.json();

      document.getElementById('buildProgressFill').style.width = data.progress + '%';
      document.getElementById('buildStatusText').textContent = data.message;

      if (data.stage) {
        updateBuildStages(data.stage);
      }

      if (data.status === 'subtitle_choice') {
        clearInterval(_pollBuildInterval);
        _pollBuildInterval = null;
        // Mark trimming and concat as done
        document.querySelectorAll('.build-stage').forEach(el => {
          const stage = el.dataset.stage;
          if (stage === 'trimming' || stage === 'concat') {
            el.classList.remove('active');
            el.classList.add('done');
            el.querySelector('.stage-icon').innerHTML = '&#x2713;';
          }
        });
        // Show subtitle choice buttons
        document.getElementById('buildProgress').style.display = 'none';
        document.getElementById('subtitleChoice').style.display = 'block';
      } else if (data.status === 'done') {
        clearInterval(_pollBuildInterval);
        _pollBuildInterval = null;
        _buildInProgress = false;
        document.querySelectorAll('.build-stage').forEach(el => {
          el.classList.remove('active');
          el.classList.add('done');
          el.querySelector('.stage-icon').innerHTML = '&#x2713;';
        });
        document.getElementById('buildProgress').style.display = 'none';
        document.getElementById('subtitleChoice').style.display = 'none';
        document.getElementById('downloadArea').style.display = 'block';
        document.getElementById('downloadInfo').textContent = data.message;
      } else if (data.status === 'error') {
        clearInterval(_pollBuildInterval);
        _pollBuildInterval = null;
        _buildInProgress = false;
      }
    } catch (e) {
      // ignore
    }
  }, 1000);
}

async function continueWithSubtitle() {
  document.getElementById('subtitleChoice').style.display = 'none';
  document.getElementById('buildProgress').style.display = 'block';
  document.getElementById('buildStatusText').textContent = t('burning_subtitle');

  try {
    var csResp = await fetch('/api/continue-build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ burn_subtitle: true }),
    });
    if (!csResp.ok) {
      var csData = await csResp.json().catch(function() { return {}; });
      document.getElementById('buildStatusText').textContent = csData.error || 'Failed (HTTP ' + csResp.status + ')';
      return;
    }
  } catch (e) {
    document.getElementById('buildStatusText').textContent = 'Network error';
    return;
  }
  pollBuild();
}

async function continueWithoutSubtitle() {
  document.getElementById('subtitleChoice').style.display = 'none';
  document.getElementById('buildProgress').style.display = 'block';
  document.getElementById('buildStatusText').textContent = t('outputting_video');

  try {
    var cnResp = await fetch('/api/continue-build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ burn_subtitle: false }),
    });
    if (!cnResp.ok) {
      var cnData = await cnResp.json().catch(function() { return {}; });
      document.getElementById('buildStatusText').textContent = cnData.error || 'Failed (HTTP ' + cnResp.status + ')';
      return;
    }
  } catch (e) {
    document.getElementById('buildStatusText').textContent = 'Network error';
    return;
  }
  pollBuild();
}

// === Helpers ===
function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  const ms = Math.floor((seconds % 1) * 10);
  return `${m}:${String(s).padStart(2, '0')}.${ms}`;
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// === Module Switching ===
let currentModule = 0; // 0=selector, 1=clip assembler, 2=remix

function showModule(n) {
  // Clean up module 2 polling timers when switching away
  if (currentModule === 2 && n !== 2 && typeof remixCleanupPolling === 'function') {
    remixCleanupPolling();
  }
  currentModule = n;
  document.getElementById('moduleSelector').style.display = n === 0 ? 'block' : 'none';
  document.getElementById('module1').style.display = n === 1 ? 'block' : 'none';
  document.getElementById('module2').style.display = n === 2 ? 'block' : 'none';

  if (n === 2 && typeof remixInit === 'function') {
    remixInit();
  }
}
