// AI Remix Module Frontend Logic
// Handles: Step navigation, asset library, script editor, compliance check, translation

// State
let remixStep = 0;
let remixMaxStep = 0;

// Polling interval registry — cleared on module switch to prevent leaks
const _remixPollingIntervals = new Set();
function _remixRegisterInterval(id) { _remixPollingIntervals.add(id); return id; }
function _remixClearInterval(id) { clearInterval(id); _remixPollingIntervals.delete(id); }
function remixCleanupPolling() {
  _remixPollingIntervals.forEach(function(id) { clearInterval(id); });
  _remixPollingIntervals.clear();
}
const REMIX_STEPS = 6; // Steps 0-5
const ZH_CHAR_LIMIT = 50;
const ID_WORD_LIMIT = 25;
let remixSegments = Array(5).fill(null).map(() => ({zh: '', id: '', zh_char_count: 0, id_word_count: 0}));

// Remix i18n strings (accessed via rt() helper)
const REMIX_I18N = {
  zh: {
    asset_ready: '素材库已就绪',
    asset_clips: '个素材',
    asset_not_init: '素材库未初始化',
    asset_check_fail: '无法检查素材库状态',
    creating: '创建中...',
    lib_created: '素材库已创建，上传素材后点击验证',
    create_fail: '创建失败: ',
    uploading: '上传中...',
    upload_fail: '上传失败',
    verifying: '验证中...',
    verify_fail: '验证失败: ',
    translating: '翻译中...',
    translate_btn: '翻译为印尼语',
    translate_fail: '翻译失败: ',
    checking: '检查中...',
    compliance_btn: '合规审核',
    compliance_fail: '合规审核失败: ',
    violations_found: '处违规',
    segment_label: '段落',
    no_violations: '未发现合规问题',
    check_complete: '审核完成',
    task_fail: '任务失败: ',
    save_fail: '保存失败: ',
    words: '词',
    chars: '字',
    input_lang_zh: '输入：中文',
    input_lang_id: '输入：印尼语',
    placeholder_zh: '输入中文文案...',
    placeholder_id: '输入印尼语文案...',
    create_library: '创建素材库',
    verify_continue: '验证并继续',
    back: '返回',
    next_script: '下一步：编写脚本',
    next_frames: '下一步：AI画面',
    upload_hint: '上传实物素材（至少2个，每个8秒）',
    generating: '生成中...',
    gen_frames: '生成首尾帧',
    frames_done: '首尾帧生成完成',
    gen_videos: '生成5个视频',
    assembling: '拼接中...',
    download: '下载视频',
    goto_subtitles: '去加字幕',
    kw_title: '关键词高亮',
    kw_desc: '选择要高亮的关键词，字幕中将放大+黄色显示。可跳过直接烧录。',
    kw_auto_detect: '自动识别',
    kw_detecting: '识别中...',
    kw_manual_label: '或手动输入中文关键词：',
    kw_manual_placeholder: '例：真的, 百万, 一天',
    kw_match: '匹配关键词',
    kw_matching: '匹配中...',
    kw_burn: '烧录字幕',
    kw_burn_skip: '跳过高亮，直接烧录',
    kw_chip_numbers: '数字',
    kw_chip_money: '金额',
    kw_chip_time: '时间',
    kw_chip_age: '年龄',
    kw_chip_brand: '品牌名',
    kw_chip_emotion: '强调词',
    next_videos: '下一步：生成视频',
    next_assembly: '下一步：拼接',
    assemble_btn: '拼接最终视频',
    assembly_desc: '16秒AI + 16秒实物素材配画外音 + 8秒CTA = 40秒',
    s3_title: 'AI首尾帧',
    s4_title: 'Seedance 视频生成',
    s5_title: '最终拼接',
    new_video: '制作新视频',
    translate_one: '翻译',
    retry: '重跑',
    frame_retry: '重跑此帧',
    frame_retry_limit: '已达上限',
    script_label: '台词',
  },
  id: {
    asset_ready: 'Perpustakaan aset siap',
    asset_clips: ' klip',
    asset_not_init: 'Perpustakaan aset belum diinisialisasi',
    asset_check_fail: 'Gagal memeriksa status perpustakaan',
    creating: 'Membuat...',
    lib_created: 'Perpustakaan dibuat. Unggah klip lalu verifikasi.',
    create_fail: 'Gagal membuat: ',
    uploading: 'Mengunggah...',
    upload_fail: 'Gagal mengunggah',
    verifying: 'Memverifikasi...',
    verify_fail: 'Gagal memverifikasi: ',
    translating: 'Menerjemahkan...',
    translate_btn: 'Terjemahkan ke Indonesia',
    translate_fail: 'Gagal menerjemahkan: ',
    checking: 'Memeriksa...',
    compliance_btn: 'Periksa Kepatuhan',
    compliance_fail: 'Gagal memeriksa: ',
    violations_found: ' pelanggaran',
    segment_label: 'Segmen',
    no_violations: 'Tidak ada masalah kepatuhan',
    check_complete: 'Pemeriksaan selesai',
    task_fail: 'Tugas gagal: ',
    save_fail: 'Gagal menyimpan: ',
    words: ' kata',
    chars: ' karakter',
    input_lang_zh: 'Input: Mandarin',
    input_lang_id: 'Input: Indonesia',
    placeholder_zh: 'Masukkan naskah dalam bahasa Mandarin...',
    placeholder_id: 'Masukkan naskah dalam bahasa Indonesia...',
    create_library: 'Buat Perpustakaan Aset',
    verify_continue: 'Verifikasi & Lanjutkan',
    back: 'Kembali',
    next_script: 'Lanjut: Tulis Naskah',
    next_frames: 'Lanjut: AI Frame',
    upload_hint: 'Unggah klip real footage (min 2, masing-masing 8 detik)',
    generating: 'Menghasilkan...',
    gen_frames: 'Buat Frame',
    frames_done: 'Frame selesai dibuat',
    gen_videos: 'Buat 5 Video',
    assembling: 'Merakit...',
    download: 'Unduh Video',
    goto_subtitles: 'Tambah Subtitle',
    kw_title: 'Sorotan Kata Kunci',
    kw_desc: 'Pilih kata kunci untuk disorot — tampil lebih besar + kuning di subtitle. Bisa dilewati.',
    kw_auto_detect: 'Deteksi Otomatis',
    kw_detecting: 'Mendeteksi...',
    kw_manual_label: 'Atau masukkan kata kunci dalam bahasa Mandarin:',
    kw_manual_placeholder: 'Contoh: beneran, juta, sehari',
    kw_match: 'Cocokkan',
    kw_matching: 'Mencocokkan...',
    kw_burn: 'Bakar Subtitle',
    kw_burn_skip: 'Lewati sorotan, langsung bakar',
    kw_chip_numbers: 'Angka',
    kw_chip_money: 'Uang',
    kw_chip_time: 'Waktu',
    kw_chip_age: 'Usia',
    kw_chip_brand: 'Merek',
    kw_chip_emotion: 'Emosi',
    next_videos: 'Lanjut: Buat Video',
    next_assembly: 'Lanjut: Perakitan',
    assemble_btn: 'Rakit Video Akhir',
    assembly_desc: '16d AI + 16d footage + suara latar + 8d CTA = 40d',
    s3_title: 'AI Frame Awal/Akhir',
    s4_title: 'Pembuatan Video Seedance',
    s5_title: 'Perakitan Akhir',
    new_video: 'Buat Video Baru',
    translate_one: 'Terjemahkan',
    retry: 'Ulangi',
    frame_retry: 'Ulangi frame',
    frame_retry_limit: 'Batas tercapai',
    script_label: 'Naskah',
  },
  en: {
    asset_ready: 'Asset library ready',
    asset_clips: ' clips',
    asset_not_init: 'Asset library not initialized',
    asset_check_fail: 'Unable to check library status',
    creating: 'Creating...',
    lib_created: 'Library created. Upload clips then verify.',
    create_fail: 'Failed to create: ',
    uploading: 'Uploading...',
    upload_fail: 'Upload failed',
    verifying: 'Verifying...',
    verify_fail: 'Verification failed: ',
    translating: 'Translating...',
    translate_btn: 'Translate to Indonesian',
    translate_fail: 'Translation failed: ',
    checking: 'Checking...',
    compliance_btn: 'Check Compliance',
    compliance_fail: 'Compliance check failed: ',
    violations_found: ' violation(s)',
    segment_label: 'Segment',
    no_violations: 'No compliance issues found',
    check_complete: 'Check complete',
    task_fail: 'Task failed: ',
    save_fail: 'Save failed: ',
    words: ' words',
    chars: ' chars',
    input_lang_zh: 'Input: Chinese',
    input_lang_id: 'Input: Indonesian',
    placeholder_zh: 'Enter Chinese script...',
    placeholder_id: 'Enter Indonesian script...',
    create_library: 'Create Asset Library',
    verify_continue: 'Verify & Continue',
    back: 'Back',
    next_script: 'Next: Write Script',
    next_frames: 'Next: AI Frames',
    upload_hint: 'Upload real footage clips (min 2, 8s each)',
    generating: 'Generating...',
    gen_frames: 'Generate Frames',
    frames_done: 'All frames generated',
    gen_videos: 'Generate 5 Videos',
    assembling: 'Assembling...',
    download: 'Download Video',
    goto_subtitles: 'Add Subtitles',
    kw_title: 'Keyword Highlight',
    kw_desc: 'Select keywords to highlight — shown larger + yellow in subtitles. You can skip this.',
    kw_auto_detect: 'Auto Detect',
    kw_detecting: 'Detecting...',
    kw_manual_label: 'Or enter Chinese keywords manually:',
    kw_manual_placeholder: 'e.g. really, million, one day',
    kw_match: 'Match Keywords',
    kw_matching: 'Matching...',
    kw_burn: 'Burn Subtitles',
    kw_burn_skip: 'Skip highlights, burn directly',
    kw_chip_numbers: 'Numbers',
    kw_chip_money: 'Money',
    kw_chip_time: 'Time',
    kw_chip_age: 'Age',
    kw_chip_brand: 'Brand',
    kw_chip_emotion: 'Emotion',
    next_videos: 'Next: Generate Videos',
    next_assembly: 'Next: Assembly',
    assemble_btn: 'Assemble Final Video',
    assembly_desc: '16s AI + 16s real footage with voiceover + 8s CTA = 40s',
    s3_title: 'AI First/Last Frames',
    s4_title: 'Seedance Video Generation',
    s5_title: 'Final Assembly',
    new_video: 'Start New Video',
    translate_one: 'Translate',
    retry: 'Retry',
    frame_retry: 'Retry frame',
    frame_retry_limit: 'Limit reached',
    script_label: 'Script',
  },
};

function rt(key) {
  const lang = typeof currentLang !== 'undefined' ? currentLang : 'zh';
  const dict = REMIX_I18N[lang] || REMIX_I18N.zh;
  return dict[key] || REMIX_I18N.zh[key] || key;
}

// Script input language toggle state
let scriptInputLang = 'zh';

// Segment labels
const SEGMENT_LABELS = [
  {type: 'ai_firstlast', zh: 'S1 过去的辛苦', id: 'S1 Masa Lalu', en: 'S1 Past Struggle'},
  {type: 'ai_firstlast', zh: 'S2 转折+现在', id: 'S2 Titik Balik', en: 'S2 Turning Point'},
  {type: 'ai_static', zh: 'S3 加入门槛', id: 'S3 Biaya Gabung', en: 'S3 Entry Cost'},
  {type: 'ai_static', zh: 'S4 裂变机制', id: 'S4 Mekanisme Fisi', en: 'S4 Fission Model'},
  {type: 'ai_static', zh: 'S5 女性赋权CTA', id: 'S5 CTA Pemberdayaan', en: 'S5 Empowerment CTA'},
];

// Badge class mapping
function getBadgeClass(type) {
  switch (type) {
    case 'ai_firstlast': return 'ai';
    case 'ai_static': return 'ai';
    case 'ai_cta': return 'cta';
    default: return 'ai';
  }
}

// Badge label mapping
function getBadgeLabel(type) {
  const labels = {
    ai_firstlast: { zh: 'AI首尾帧', id: 'AI First/Last', en: 'AI First/Last' },
    ai_static: { zh: 'AI静态', id: 'AI Static', en: 'AI Static' },
    ai_cta: { zh: 'CTA', id: 'CTA', en: 'CTA' },
  };
  const lang = typeof currentLang !== 'undefined' ? currentLang : 'zh';
  return (labels[type] && labels[type][lang]) || type;
}

// Duration per segment (seconds)
const SEGMENT_DURATIONS = [8, 8, 8, 8, 8];

// === Step Navigation ===
function remixGoToStep(n) {
  remixStep = n;
  if (n > remixMaxStep) remixMaxStep = n;
  // Persist step to localStorage so page refresh restores current step
  localStorage.setItem('remix_current_step', String(n));
  localStorage.setItem('remix_max_step', String(remixMaxStep));
  for (let i = 0; i < REMIX_STEPS; i++) {
    const el = document.getElementById('remixStep' + i);
    if (el) el.classList.toggle('active', i === n);
  }
  remixRenderNavDots();

  // Render script editor when entering step 2
  if (n === 2) {
    renderScriptEditor();
  }

  // Show start button when entering step 4 (user picks resolution first)
  if (n === 4) {
    var startBtn = document.getElementById('btnStartSeedance');
    if (startBtn) startBtn.style.display = 'inline-flex';
  }

}

function remixRenderNavDots() {
  const container = document.getElementById('remixNavDots');
  if (!container) return;
  container.innerHTML = '';
  for (let i = 0; i < REMIX_STEPS; i++) {
    const dot = document.createElement('div');
    dot.className = 'nav-dot';
    if (i === remixStep) dot.classList.add('active');
    if (i < remixStep) dot.classList.add('done');
    if (i !== remixStep && i <= remixMaxStep) {
      dot.style.cursor = 'pointer';
      dot.addEventListener('click', ((step) => () => remixGoToStep(step))(i));
    }
    container.appendChild(dot);
  }
}

// === Remix Init ===
var _remixInitDone = false;
async function remixInit() {
  if (_remixInitDone) return;
  _remixInitDone = true;
  // Restore step from localStorage (persist across page refresh)
  var savedStep = parseInt(localStorage.getItem('remix_current_step') || '0', 10);
  var savedMaxStep = parseInt(localStorage.getItem('remix_max_step') || '0', 10);
  remixMaxStep = savedMaxStep;
  remixGoToStep(savedStep);
  remixCheckLibraryStatus();
  remixSetupUpload();

  // If returning to step 4+, verify backend session still has data
  if (savedStep >= 4) {
    try {
      var chk = await fetch('/api/remix/seedance-status');
      var chkData = await chk.json();
      var hasData = chkData.segments && chkData.segments.some(function(s) { return s.status !== 'pending'; });
      if (hasData) {
        if (savedStep === 4) {
          _seedanceLastFingerprint = '';
          remixPollSeedance();
        }
      } else {
        // Backend session lost (e.g. after redeploy), fall back to step 2
        remixGoToStep(2);
      }
    } catch (e) {
      remixGoToStep(2);
    }
  }

  // Restore from localStorage if available
  var saved = localStorage.getItem('remix_segments');
  if (saved) {
    try {
      var parsed = JSON.parse(saved);
      if (Array.isArray(parsed) && parsed.length === 5) {
        remixSegments = parsed;
        return; // Skip fetching defaults if we have saved data
      }
    } catch(e) { /* ignore parse errors */ }
  }

  // Load default scripts
  try {
    const resp = await fetch('/api/remix/defaults');
    const data = await resp.json();
    if (data.segments) {
      data.segments.forEach((seg, idx) => {
        if (idx < remixSegments.length) {
          remixSegments[idx].zh = seg.default_zh || '';
          remixSegments[idx].id = seg.default_id || '';
          remixSegments[idx].zh_char_count = (seg.default_zh || '').length;
          remixSegments[idx].id_word_count = (seg.default_id || '').trim().split(/\s+/).filter(Boolean).length;
        }
      });
    }
  } catch (e) { /* defaults not critical */ }
}

async function remixCheckLibraryStatus() {
  try {
    const resp = await fetch('/api/remix/library-status');
    const data = await resp.json();
    const statusEl = document.getElementById('libraryStatus');
    if (data.initialized) {
      statusEl.innerHTML = '<div class="violation-summary clean"><span class="violation-icon">&#x2705;</span> ' + rt('asset_ready') + ' (' + (data.clip_count || 0) + rt('asset_clips') + ')</div>';
      document.getElementById('btnInitLib').style.display = 'none';
      document.getElementById('btnFinalizeLib').style.display = 'none';
      document.getElementById('btnSkipToScript').style.display = 'inline-flex';
      // Allow proceeding
      remixMaxStep = Math.max(remixMaxStep, 5);
      remixRenderNavDots();
    } else {
      statusEl.innerHTML = '<div class="violation-summary warning"><span class="violation-icon">&#x26A0;&#xFE0F;</span> ' + rt('asset_not_init') + '</div>';
    }
  } catch (e) {
    // API might not exist yet, that's ok
    const statusEl = document.getElementById('libraryStatus');
    if (statusEl) {
      statusEl.innerHTML = '<div class="violation-summary warning"><span class="violation-icon">&#x26A0;&#xFE0F;</span> ' + rt('asset_check_fail') + '</div>';
    }
  }
  remixLoadServerClips();
}

// === Server Clip Management ===
async function remixLoadServerClips() {
  try {
    var resp = await fetch('/api/remix/list-clips');
    var data = await resp.json();
    var list = document.getElementById('serverClipList');
    if (!list) return;
    if (!data.clips || data.clips.length === 0) { list.innerHTML = ''; return; }
    var html = '<div style="font-size:13px;color:#888;margin-bottom:4px;">' +
      (typeof remixLang !== 'undefined' && remixLang === 'zh' ? '服务器已有素材：' : 'Server clips:') + '</div>';
    for (var i = 0; i < data.clips.length; i++) {
      var c = data.clips[i];
      var safeName = (c.filename || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      var safeNameJs = safeName.replace(/'/g,"\\'").replace(/"/g,'&quot;');
      html += '<div class="file-item">' +
        '<span class="name">' + safeName + '</span>' +
        '<span class="size">' + (c.size_mb || 0) + ' MB</span>' +
        '<span style="cursor:pointer;color:#f66;margin-left:8px;font-size:16px;" onclick="remixDeleteServerClip(\'' + safeNameJs + '\')">\u{1F5D1}</span>' +
        '</div>';
    }
    list.innerHTML = html;
  } catch (e) { console.error('[serverClips]', e); }
}

async function remixDeleteServerClip(filename) {
  var _lang = typeof currentLang !== 'undefined' ? currentLang : 'zh';
  if (!confirm((_lang === 'zh' ? '确定删除 ' : 'Delete ') + filename + '?')) return;
  try {
    const resp = await fetch('/api/remix/delete-clip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: filename }),
    });
    const data = await resp.json();
    if (data.error) { alert(data.error); return; }
    remixLoadServerClips();
    remixCheckLibraryStatus();
  } catch (e) {
    alert('Delete failed: ' + e.message);
  }
}

// === Upload ===
let remixPendingFiles = [];

function remixSetupUpload() {
  const area = document.getElementById('remixUploadArea');
  if (!area) return;

  // Remove old listeners by cloning
  const newArea = area.cloneNode(true);
  area.parentNode.replaceChild(newArea, area);

  newArea.addEventListener('click', () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = 'video/*';
    input.style.display = 'none';
    input.addEventListener('change', () => {
      remixHandleFiles(input.files);
      input.remove();
    });
    document.body.appendChild(input);
    input.click();
  });

  newArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    newArea.classList.add('dragover');
  });

  newArea.addEventListener('dragleave', () => {
    newArea.classList.remove('dragover');
  });

  newArea.addEventListener('drop', (e) => {
    e.preventDefault();
    newArea.classList.remove('dragover');
    remixHandleFiles(e.dataTransfer.files);
  });
}

function remixHandleFiles(fileList) {
  const newFiles = Array.from(fileList).filter(f =>
    f.type.startsWith('video/') || f.name.match(/\.(mp4|mov|webm|avi|mkv)$/i)
  );
  for (const nf of newFiles) {
    const dup = remixPendingFiles.some(pf => pf.name === nf.name && pf.size === nf.size);
    if (!dup) remixPendingFiles.push(nf);
  }
  remixRenderFileList();
}

function remixRenderFileList() {
  const list = document.getElementById('remixFileList');
  if (!list) return;
  list.innerHTML = '';
  remixPendingFiles.forEach((f, i) => {
    const div = document.createElement('div');
    div.className = 'file-item';
    const sizeMB = (f.size / 1024 / 1024).toFixed(1);
    div.innerHTML = '<span class="name">' + escapeHtml(f.name) + '</span>' +
      '<span class="size">' + sizeMB + ' MB</span>' +
      '<span class="remove-btn" onclick="remixRemoveFile(' + i + ')" style="cursor:pointer;color:#f66;margin-left:8px;">&#x2715;</span>';
    list.appendChild(div);
  });
}

function remixRemoveFile(index) {
  remixPendingFiles.splice(index, 1);
  remixRenderFileList();
}

// === Init Library ===
async function remixInitLibrary() {
  const btn = document.getElementById('btnInitLib');
  btn.disabled = true;
  btn.textContent = rt('creating');

  try {
    // Init + upload + finalize in one go
    const resp = await fetch('/api/remix/init-library', { method: 'POST' });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    // Upload pending files
    if (remixPendingFiles.length > 0) {
      btn.textContent = rt('uploading') || 'Uploading...';
      await remixUploadClip();
    }

    // Auto-finalize
    const fResp = await fetch('/api/remix/finalize-library', { method: 'POST' });
    if (!fResp.ok) throw new Error('HTTP ' + fResp.status);
    const fData = await fResp.json();
    if (fData.error) throw new Error(fData.error);

    const statusEl = document.getElementById('libraryStatus');
    statusEl.innerHTML = '<div class="violation-summary clean"><span class="violation-icon">&#x2705;</span> ' + rt('asset_ready') + ' (' + (fData.clip_count || 0) + rt('asset_clips') + ')</div>';
    btn.style.display = 'none';
    document.getElementById('btnFinalizeLib').style.display = 'none';
    document.getElementById('btnSkipToScript').style.display = 'inline-flex';
    remixMaxStep = Math.max(remixMaxStep, 5);
    remixRenderNavDots();
  } catch (err) {
    alert(rt('create_fail') + err.message);
    btn.disabled = false;
    btn.textContent = rt('create_library');
  }
}

// === Upload Clip ===
async function remixUploadClip() {
  if (remixPendingFiles.length === 0) return;

  const total = remixPendingFiles.length;
  for (let i = 0; i < total; i++) {
    const f = remixPendingFiles[i];
    try {
      const resp = await fetch('/api/remix/upload-clip', {
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
    } catch (err) {
      alert(rt('upload_fail') + ' (' + f.name + '): ' + err.message);
      return;
    }
  }

  // Mark uploads complete
  const list = document.getElementById('remixFileList');
  list.innerHTML = '';
  remixPendingFiles.forEach(f => {
    const div = document.createElement('div');
    div.className = 'file-item';
    div.innerHTML = '<span class="check">&#x2713;</span> <span class="name">' + escapeHtml(f.name) + '</span>';
    list.appendChild(div);
  });
  remixPendingFiles = [];
}

// === Finalize Library ===
async function remixFinalizeLibrary() {
  const btn = document.getElementById('btnFinalizeLib');
  btn.disabled = true;
  btn.textContent = rt('verifying');

  // Upload pending files first
  if (remixPendingFiles.length > 0) {
    await remixUploadClip();
  }

  try {
    const resp = await fetch('/api/remix/finalize-library', { method: 'POST' });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    const statusEl = document.getElementById('libraryStatus');
    statusEl.innerHTML = '<div class="violation-summary clean"><span class="violation-icon">&#x2705;</span> ' + rt('asset_ready') + ' (' + (data.clip_count || 0) + rt('asset_clips') + ')</div>';
    btn.style.display = 'none';

    // Allow proceeding
    remixMaxStep = Math.max(remixMaxStep, 1);
    remixRenderNavDots();
    remixGoToStep(1);
  } catch (err) {
    alert(rt('verify_fail') + err.message);
    btn.disabled = false;
    btn.textContent = rt('verify_continue');
  }
}

// === Script Input Language Toggle ===
function setScriptLang(lang) {
  // Save current text to appropriate field first
  document.querySelectorAll('.script-textarea').forEach(ta => {
    const idx = parseInt(ta.dataset.idx);
    if (scriptInputLang === 'zh') {
      remixSegments[idx].zh = ta.value;
    } else {
      remixSegments[idx].id = ta.value;
    }
  });
  scriptInputLang = lang;
  renderScriptEditor();
}

// === Script Editor (Step 2) ===
function renderScriptEditor() {
  const container = document.getElementById('scriptEditor');
  if (!container) return;
  container.innerHTML = '';

  const lang = typeof currentLang !== 'undefined' ? currentLang : 'zh';

  // Language toggle
  let toggleHtml = '<div style="display:flex;gap:8px;margin-bottom:12px;">' +
    '<button class="btn ' + (scriptInputLang === 'zh' ? 'btn-primary' : 'btn-secondary') + ' btn-sm" onclick="setScriptLang(\'zh\')">' + rt('input_lang_zh') + '</button>' +
    '<button class="btn ' + (scriptInputLang === 'id' ? 'btn-primary' : 'btn-secondary') + ' btn-sm" onclick="setScriptLang(\'id\')">' + rt('input_lang_id') + '</button>' +
    '</div>';
  var toggleDiv = document.createElement('div');
  toggleDiv.innerHTML = toggleHtml;
  container.appendChild(toggleDiv);

  remixSegments.forEach((seg, idx) => {
    const label = SEGMENT_LABELS[idx];
    const badgeClass = getBadgeClass(label.type);
    const badgeLabel = getBadgeLabel(label.type);
    const segLabel = label[lang] || label.en;
    const duration = SEGMENT_DURATIONS[idx];

    const div = document.createElement('div');
    div.className = 'script-segment';

    let html = '<div class="segment-header">' +
      '<span class="segment-badge ' + badgeClass + '">' + badgeLabel + '</span>' +
      '<span class="segment-label">' + escapeHtml(segLabel) + '</span>';
    if (duration > 0) {
      html += '<span class="segment-duration">' + duration + 's</span>';
    }
    html += '</div>';

    // Textarea content based on input language
    const textValue = scriptInputLang === 'zh' ? seg.zh : seg.id;
    const placeholder = rt(scriptInputLang === 'zh' ? 'placeholder_zh' : 'placeholder_id');

    if (scriptInputLang === 'zh') {
      const zhCount = textValue ? textValue.length : 0;
      const zhOver = zhCount > ZH_CHAR_LIMIT;
      html += '<textarea class="script-textarea' + (zhOver ? ' over-limit' : '') + '" ' +
        'data-idx="' + idx + '" ' +
        'placeholder="' + escapeHtml(placeholder) + '" ' +
        'oninput="updateCharCount(' + idx + ')">' + escapeHtml(textValue) + '</textarea>';
      html += '<div class="char-count' + (zhOver ? ' over' : '') + '" id="charCount' + idx + '">' +
        zhCount + ' / ' + ZH_CHAR_LIMIT + rt('chars') + '</div>';
    } else {
      const idWords = textValue ? textValue.trim().split(/\s+/).filter(Boolean).length : 0;
      const idOver = idWords > ID_WORD_LIMIT;
      html += '<textarea class="script-textarea' + (idOver ? ' over-limit' : '') + '" ' +
        'data-idx="' + idx + '" ' +
        'placeholder="' + escapeHtml(placeholder) + '" ' +
        'oninput="updateCharCount(' + idx + ')">' + escapeHtml(textValue) + '</textarea>';
      html += '<div class="char-count' + (idOver ? ' over' : '') + '" id="charCount' + idx + '">' +
        idWords + ' / ' + ID_WORD_LIMIT + rt('words') + '</div>';
    }

    // Per-segment translate button + Indonesian translation
    if (scriptInputLang === 'zh') {
      html += '<div style="display:flex;align-items:center;gap:6px;margin-top:4px;">' +
        '<button class="btn btn-secondary btn-sm" id="btnTransOne' + idx + '" onclick="remixTranslateOne(' + idx + ')" style="padding:3px 10px;font-size:11px;">翻译</button>' +
        '</div>';
      if (seg.id) {
        const idWords = seg.id.trim().split(/\s+/).filter(Boolean).length;
        const idOver = idWords > ID_WORD_LIMIT;
        html += '<div class="id-translation">' +
          '<div>' + escapeHtml(seg.id) + '</div>' +
          '<div class="word-count' + (idOver ? ' over' : '') + '">' + idWords + ' / ' + ID_WORD_LIMIT + rt('words') + '</div>' +
          '</div>';
      }
    }

    div.innerHTML = html;
    container.appendChild(div);
  });
}

function updateCharCount(idx) {
  const textarea = document.querySelector('.script-textarea[data-idx="' + idx + '"]');
  if (!textarea) return;
  const text = textarea.value;

  if (scriptInputLang === 'zh') {
    const count = text.length;
    remixSegments[idx].zh = text;
    remixSegments[idx].zh_char_count = count;
    const countEl = document.getElementById('charCount' + idx);
    if (countEl) {
      countEl.textContent = count + ' / ' + ZH_CHAR_LIMIT + rt('chars');
      countEl.className = count > ZH_CHAR_LIMIT ? 'char-count over' : 'char-count';
      textarea.className = 'script-textarea' + (count > ZH_CHAR_LIMIT ? ' over-limit' : '');
    }
  } else {
    const words = text.trim().split(/\s+/).filter(Boolean).length;
    remixSegments[idx].id = text;
    remixSegments[idx].id_word_count = words;
    const countEl = document.getElementById('charCount' + idx);
    if (countEl) {
      countEl.textContent = words + ' / ' + ID_WORD_LIMIT + rt('words');
      countEl.className = words > ID_WORD_LIMIT ? 'char-count over' : 'char-count';
      textarea.className = 'script-textarea' + (words > ID_WORD_LIMIT ? ' over-limit' : '');
    }
  }

  // Persist to localStorage
  localStorage.setItem('remix_segments', JSON.stringify(remixSegments));
}

// === Save Script ===
async function remixSaveScript() {
  // Collect all segments from text areas
  document.querySelectorAll('.script-textarea').forEach(ta => {
    const idx = parseInt(ta.dataset.idx);
    if (scriptInputLang === 'zh') {
      remixSegments[idx].zh = ta.value;
      remixSegments[idx].zh_char_count = ta.value.length;
    } else {
      remixSegments[idx].id = ta.value;
      remixSegments[idx].id_word_count = ta.value.trim().split(/\s+/).filter(Boolean).length;
    }
  });

  try {
    const resp = await fetch('/api/remix/save-script', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ segments: remixSegments }),
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    if (data.error) throw new Error(data.error);
    return true;
  } catch (err) {
    alert(rt('save_fail') + err.message);
    return false;
  }
}

function remixSaveAndNext() {
  remixSaveScript().then(ok => {
    if (ok) remixGoToStep(3);
  });
}

// === Translate ===
async function remixTranslate() {
  const btn = document.getElementById('btnTranslate');
  if (btn) { btn.disabled = true; btn.textContent = rt('translating'); }

  // Save first
  document.querySelectorAll('.script-textarea').forEach(ta => {
    const idx = parseInt(ta.dataset.idx);
    if (scriptInputLang === 'zh') {
      remixSegments[idx].zh = ta.value;
    } else {
      remixSegments[idx].id = ta.value;
    }
  });

  try {
    const resp = await fetch('/api/remix/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ segments: remixSegments }),
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    if (data.status === 'processing') {
      // Poll for completion
      remixPollStatus('translate', () => {
        if (btn) { btn.disabled = false; btn.textContent = rt('translate_btn'); }
      });
    } else if (data.translations) {
      // Direct result
      data.translations.forEach((t, idx) => {
        if (idx < remixSegments.length) {
          remixSegments[idx].id = t;
          remixSegments[idx].id_word_count = t.trim().split(/\s+/).filter(Boolean).length;
        }
      });
      renderScriptEditor();
      if (btn) { btn.disabled = false; btn.textContent = rt('translate_btn'); }
    }
  } catch (err) {
    alert(rt('translate_fail') + err.message);
    if (btn) { btn.disabled = false; btn.textContent = rt('translate_btn'); }
  }
}

// === Compliance Check ===
async function remixCheckCompliance() {
  const btn = document.getElementById('btnCompliance');
  btn.disabled = true;
  btn.textContent = rt('checking');

  // Collect current text
  document.querySelectorAll('.script-textarea').forEach(ta => {
    const idx = parseInt(ta.dataset.idx);
    if (scriptInputLang === 'zh') {
      remixSegments[idx].zh = ta.value;
    } else {
      remixSegments[idx].id = ta.value;
    }
  });

  try {
    const resp = await fetch('/api/remix/check-compliance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ segments: remixSegments }),
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    const resultEl = document.getElementById('complianceResult');

    if (data.violations && data.violations.length > 0) {
      const totalCount = data.violation_count || data.violations.reduce((sum, v) => sum + (v.issues ? v.issues.length : 1), 0);
      let html = '<div class="violation-summary warning"><span class="violation-icon">&#x26A0;&#xFE0F;</span> ' +
        totalCount + rt('violations_found') + '</div>';
      data.violations.forEach(v => {
        const issues = v.issues || [v];
        issues.forEach(issue => {
          html += '<div class="script-segment" style="border-color:#fde0d8;background:#fff8f6;">' +
            '<strong>' + rt('segment_label') + ' ' + (v.segment + 1) + ':</strong> ' +
            '<span class="violation-word">' + escapeHtml(issue.word || '') + '</span> ' +
            '<span style="color:#8e8e8e;font-size:12px;">(' + escapeHtml(issue.category || '') + ')</span>' +
            '</div>';
        });
      });
      resultEl.innerHTML = html;
    } else if (data.clean) {
      resultEl.innerHTML = '<div class="violation-summary clean"><span class="violation-icon">&#x2705;</span> ' + rt('no_violations') + '</div>';
    } else {
      // May need polling
      if (data.status === 'processing') {
        remixPollStatus('compliance', () => {
          btn.disabled = false;
          btn.textContent = rt('compliance_btn');
        });
        return;
      }
      resultEl.innerHTML = '<div class="violation-summary clean"><span class="violation-icon">&#x2705;</span> ' + rt('check_complete') + '</div>';
    }
  } catch (err) {
    alert(rt('compliance_fail') + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = rt('compliance_btn');
  }
}

// === Poll Status ===
function remixPollStatus(taskType, onComplete) {
  const interval = _remixRegisterInterval(setInterval(async () => {
    try {
      const resp = await fetch('/api/remix/status');
      const data = await resp.json();

      // Stop polling if task finished or nothing is running
      if (data.status === 'idle') {
        _remixClearInterval(interval);
        return;
      }

      if (data.status === 'done') {
        _remixClearInterval(interval);

        if (taskType === 'translate' && data.segments) {
          data.segments.forEach((seg, idx) => {
            if (idx < remixSegments.length && seg.id) {
              remixSegments[idx].id = seg.id;
              remixSegments[idx].id_word_count = seg.id.trim().split(/\s+/).filter(Boolean).length;
            }
          });
          renderScriptEditor();
        }

        if (taskType === 'compliance' && data.violations) {
          const resultEl = document.getElementById('complianceResult');
          if (data.violations.length > 0) {
            const totalCount = data.violation_count || data.violations.reduce((sum, v) => sum + (v.issues ? v.issues.length : 1), 0);
            let html = '<div class="violation-summary warning"><span class="violation-icon">&#x26A0;&#xFE0F;</span> ' +
              totalCount + rt('violations_found') + '</div>';
            data.violations.forEach(v => {
              const issues = v.issues || [v];
              issues.forEach(issue => {
                html += '<div class="script-segment" style="border-color:#fde0d8;background:#fff8f6;">' +
                  '<strong>' + rt('segment_label') + ' ' + (v.segment + 1) + ':</strong> ' +
                  '<span class="violation-word">' + escapeHtml(issue.word || '') + '</span> ' +
                  '<span style="color:#8e8e8e;font-size:12px;">(' + escapeHtml(issue.category || '') + ')</span>' +
                  '</div>';
              });
            });
            resultEl.innerHTML = html;
          } else {
            resultEl.innerHTML = '<div class="violation-summary clean"><span class="violation-icon">&#x2705;</span> ' + rt('no_violations') + '</div>';
          }
        }

        if (onComplete) onComplete();
      } else if (data.status === 'error') {
        _remixClearInterval(interval);
        alert(rt('task_fail') + (data.message || 'Unknown error'));
        if (onComplete) onComplete();
      }
    } catch (e) {
      // ignore polling errors
    }
  }, 1500));
}

// === Phase 2: Frame Generation (Step 3) ===
var FRAME_LABELS = {
  '0': {zh: '帧 1', id: 'Frame 1', en: 'Frame 1'},
  '1': {zh: '帧 2', id: 'Frame 2', en: 'Frame 2'},
  '2': {zh: '帧 3', id: 'Frame 3', en: 'Frame 3'},
  '3': {zh: '帧 4', id: 'Frame 4', en: 'Frame 4'},
};

function frameLabel(key) {
  var lang = typeof currentLang !== 'undefined' ? currentLang : 'zh';
  var labels = FRAME_LABELS[key];
  return labels ? (labels[lang] || labels.en) : key;
}

async function remixGenerateFrames() {
  var btn = document.getElementById('btnGenFrames');
  if (btn) { btn.disabled = true; btn.textContent = rt('generating'); }
  document.getElementById('frameGallery').innerHTML = '';

  try {
    var resp = await fetch('/api/remix/generate-frames', { method: 'POST' });
    var data = await resp.json();
    if (!resp.ok || data.error) {
      alert(data.error || 'Frame generation failed');
      if (btn) { btn.disabled = false; btn.textContent = rt('gen_frames'); }
      return;
    }
    remixPollFrames();
  } catch (err) {
    alert('Frame generation failed: ' + err.message);
    if (btn) { btn.disabled = false; btn.textContent = rt('gen_frames'); }
  }
}

function remixPollFrames() {
  var interval = _remixRegisterInterval(setInterval(async function() {
    try {
      var resp = await fetch('/api/remix/status');
      var data = await resp.json();

      if (data.status === 'idle') { _remixClearInterval(interval); return; }

      var progressEl = document.getElementById('frameProgress');
      if (progressEl) {
        progressEl.innerHTML = '<div class="progress-bar"><div class="fill" style="width:' + data.progress + '%"></div></div>' +
          '<p class="status-text">' + escapeHtml(data.message || '') + '</p>';
      }

      if (data.status === 'done') {
        _remixClearInterval(interval);
        if (progressEl) progressEl.innerHTML = '';
        var btn = document.getElementById('btnGenFrames');
        if (btn) { btn.disabled = false; btn.textContent = rt('gen_frames'); }
        document.getElementById('btnToSeedance').style.display = 'inline-flex';
        renderFrameGallery();
      } else if (data.status === 'error') {
        _remixClearInterval(interval);
        alert(rt('task_fail') + data.message);
        var btn2 = document.getElementById('btnGenFrames');
        if (btn2) { btn2.disabled = false; btn2.textContent = rt('gen_frames'); }
      }
    } catch (e) { /* ignore polling errors */ }
  }, 1500));
}

async function renderFrameGallery() {
  var container = document.getElementById('frameGallery');
  if (!container) return;

  try {
    var resp = await fetch('/api/remix/frame-status');
    var data = await resp.json();
    if (!data.frames || !data.frames.length) return;

    var html = '<div class="frame-gallery">';
    data.frames.forEach(function(f) {
      var key = '' + f.chain_idx;
      var label = frameLabel(key);
      var retries = f.retries || 0;
      var maxR = f.max_retries || 3;
      var exhausted = retries >= maxR;
      var badgeClass = exhausted ? 'retry-badge exhausted' : 'retry-badge';
      var ts = Date.now();

      html += '<div class="frame-card" id="fc_' + key + '">';
      html += '<div class="frame-card-header"><span>' + escapeHtml(label) + '</span><span class="' + badgeClass + '">(' + retries + '/' + maxR + ')</span></div>';

      if (f.status === 'done') {
        html += '<img src="/api/remix/frame-image?idx=' + f.chain_idx + '&t=' + ts + '" alt="' + escapeHtml(label) + '">';
      } else if (f.status === 'error') {
        html += '<div class="frame-error">' + escapeHtml(f.error || 'Generation failed') + '</div>';
      } else {
        html += '<div class="frame-loading">...</div>';
      }

      // Retry button (for both done and error frames)
      if (f.status === 'done' || f.status === 'error') {
        if (exhausted) {
          html += '<button class="btn-retry-frame" disabled>' + rt('frame_retry_limit') + '</button>';
        } else {
          html += '<button class="btn-retry-frame" id="frame_retry_' + f.chain_idx + '" onclick="regenerateFrame(' + f.chain_idx + ')">' + rt('frame_retry') + '</button>';
        }
      }

      html += '</div>';
    });
    html += '</div>';
    container.innerHTML = html;
  } catch (e) {
    console.error('renderFrameGallery error:', e);
  }
}

async function regenerateFrame(chainIdx) {
  var btn = document.getElementById('frame_retry_' + chainIdx);
  if (btn) { btn.disabled = true; btn.textContent = '...'; }
  try {
    var resp = await fetch('/api/remix/regenerate-frame', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chain_idx: chainIdx, feedback: '' }),
    });
    var data = await resp.json();
    if (!resp.ok || data.error) {
      alert(data.message || data.error);
      if (btn) { btn.disabled = false; btn.textContent = rt('frame_retry'); }
      return;
    }
    // Refresh gallery to show new image
    await renderFrameGallery();
  } catch (e) {
    alert('Retry failed: ' + e.message);
    if (btn) { btn.disabled = false; btn.textContent = rt('frame_retry'); }
  }
}

async function remixStartNew() {
  try {
    var rstResp = await fetch('/api/remix/reset', { method: 'POST' });
    if (!rstResp.ok) console.error('Reset failed:', rstResp.status);
    // Clear persisted state
    localStorage.removeItem('remix_current_step');
    localStorage.removeItem('remix_max_step');
    // Keep remix_segments — user doesn't want to re-enter script text
    _seedanceLastFingerprint = '';
    remixCleanupPolling();

    // Reset JS state
    remixSegments = Array(5).fill(null).map(function() { return {zh: '', id: '', zh_char_count: 0, id_word_count: 0}; });
    remixMaxStep = 0;
    remixStep = 0;

    // Clear all dynamic DOM content from previous run
    var clearIds = ['frameProgress', 'frameGallery', 'seedanceProgress', 'assemblyProgress', 'scriptEditor', 'complianceResult'];
    clearIds.forEach(function(id) {
      var el = document.getElementById(id);
      if (el) el.innerHTML = '';
    });
    var assemblyDone = document.getElementById('assemblyDone');
    if (assemblyDone) { assemblyDone.innerHTML = ''; assemblyDone.style.display = 'none'; }

    // Re-show buttons that were hidden
    var btnGenFrames = document.getElementById('btnGenFrames');
    if (btnGenFrames) { btnGenFrames.style.display = 'inline-flex'; btnGenFrames.disabled = false; }
    var btnToSeedance = document.getElementById('btnToSeedance');
    if (btnToSeedance) btnToSeedance.style.display = 'none';
    var btnStartSeedance = document.getElementById('btnStartSeedance');
    if (btnStartSeedance) { btnStartSeedance.style.display = 'inline-flex'; btnStartSeedance.disabled = false; }
    var btnToAssembly = document.getElementById('btnToAssembly');
    if (btnToAssembly) btnToAssembly.style.display = 'none';
    var btnAssemble = document.getElementById('btnAssemble');
    if (btnAssemble) { btnAssemble.style.display = 'inline-flex'; btnAssemble.disabled = false; }

    // Re-init (load defaults, check library, etc.)
    _remixInitDone = false;
    remixInit();
  } catch (e) {
    window.location.reload();
  }
}

async function retrySeedanceSegment(idx) {
  var ta = document.getElementById('seedance_script_' + idx);
  var newScript = ta ? ta.value.trim() : '';
  var body = {idx: idx};
  if (newScript) body.new_script = newScript;

  // Reset fingerprint so poll will re-render after retry
  _seedanceLastFingerprint = '';

  // Disable retry button during request
  var btn = document.getElementById('seedance_retry_' + idx);
  if (btn) { btn.disabled = true; btn.textContent = '...'; }

  try {
    var resp = await fetch('/api/remix/retry-seedance', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body),
    });
    var data = await resp.json();
    if (!resp.ok || data.error) {
      alert(data.error || 'Retry failed');
      if (btn) { btn.disabled = false; btn.textContent = rt('retry'); }
      return;
    }
    remixPollSeedance();
  } catch (e) {
    alert('Retry failed: ' + e.message);
    if (btn) { btn.disabled = false; btn.textContent = rt('retry'); }
  }
}

// === Phase 3: Seedance Video Generation (Step 4) ===
async function remixStartSeedance() {
  var btn = document.getElementById('btnStartSeedance');
  if (btn && btn.disabled) return; // prevent double-click
  if (btn) { btn.disabled = true; btn.textContent = rt('generating'); }

  try {
    // Sync Step 4 textarea edits back to remixSegments before sending
    for (var si = 0; si < 5; si++) {
      var ta = document.getElementById('seedance_script_' + si);
      if (ta && ta.value.trim()) {
        remixSegments[si].id = ta.value.trim();
      }
    }

    var res = (document.getElementById('seedanceResolution') || {}).value || '720p';
    var resp = await fetch('/api/remix/start-seedance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ segments: remixSegments, resolution: res }),
    });
    var data = await resp.json();
    if (!resp.ok || data.error) {
      alert(data.error || 'Seedance generation failed');
      if (btn) { btn.disabled = false; btn.textContent = rt('gen_videos'); }
      return;
    }
    _seedanceLastFingerprint = '';
    remixPollSeedance();
  } catch (err) {
    alert('Seedance generation failed: ' + err.message);
    if (btn) { btn.disabled = false; btn.textContent = rt('gen_videos'); }
  }
}

// Track last known status fingerprint to skip unnecessary DOM rewrites
var _seedanceLastFingerprint = '';

function remixPollSeedance() {
  var interval = _remixRegisterInterval(setInterval(async function() {
    try {
      var resp = await fetch('/api/remix/seedance-status');
      var data = await resp.json();

      if (data.status === 'idle') { _remixClearInterval(interval); return; }

      // Build fingerprint from segment statuses + progress to detect changes
      var fingerprint = data.segments ? data.segments.map(function(s) {
        return s.status + ':' + s.progress;
      }).join('|') : '';

      // Skip DOM rewrite if nothing changed (prevents video reload flood)
      if (fingerprint === _seedanceLastFingerprint) return;
      _seedanceLastFingerprint = fingerprint;

      var container = document.getElementById('seedanceProgress');
      if (container && data.segments) {
        // Save textarea values before DOM rewrite
        var savedScripts = {};
        for (var si = 0; si < 5; si++) {
          var existTa = document.getElementById('seedance_script_' + si);
          if (existTa) savedScripts[si] = existTa.value;
        }

        var html = '';
        data.segments.forEach(function(seg, idx) {
          var label = SEGMENT_LABELS[idx] ? (SEGMENT_LABELS[idx][typeof currentLang !== 'undefined' ? currentLang : 'zh'] || SEGMENT_LABELS[idx].en) : ('Segment ' + (idx+1));
          var statusIcon = seg.status === 'done' ? '&#x2705;' :
                          seg.status === 'error' ? '&#x274C;' :
                          seg.status === 'generating' ? '&#x23F3;' : '&#x25CB;';
          var pct = seg.progress || 0;
          var isActive = seg.status === 'generating' || seg.status === 'starting';

          html += '<div class="seedance-card">' +
            '<div class="seedance-card-header">' +
            '<span>' + statusIcon + ' ' + escapeHtml(label) + '</span>' +
            '<span class="seedance-pct">' + pct + '%</span>' +
            '</div>' +
            '<div class="progress-bar"><div class="fill" style="width:' + pct + '%"></div></div>' +
            (seg.message ? '<p class="status-text" style="font-size:11px;">' + escapeHtml(seg.message) + '</p>' : '');

          // Script textarea (editable, always shown)
          var scriptVal = seg.script || '';
          var taVal = (idx in savedScripts) ? savedScripts[idx] : scriptVal;

          html += '<div class="seedance-script-row">' +
            '<label style="font-size:11px;color:#8e8e8e;">' + rt('script_label') + ':</label>' +
            '<textarea id="seedance_script_' + idx + '" class="seedance-script-ta" rows="2"' +
            (isActive ? ' disabled' : '') + '>' + escapeHtml(taVal) + '</textarea>' +
            '</div>';

          // Video preview (when done) — no timestamp to prevent reload on every poll
          if (seg.status === 'done' && seg.has_video) {
            html += '<video class="seedance-preview" controls preload="metadata"' +
              ' src="/api/remix/download-segment?idx=' + idx + '">' +
              '</video>';
          }

          if (seg.error) {
            html += '<p style="color:#e74c3c;font-size:11px;">' + escapeHtml(seg.error) + '</p>';
          }

          if (seg.status === 'done' || seg.status === 'error') {
            html += '<button id="seedance_retry_' + idx + '" class="btn-retry-seg" onclick="retrySeedanceSegment(' + idx + ')">' + rt('retry') + '</button>';
          }

          html += '</div>';
        });
        container.innerHTML = html;
      }

      if (data.all_done) {
        _remixClearInterval(interval);
        var btn = document.getElementById('btnStartSeedance');
        if (btn) { btn.disabled = false; btn.textContent = rt('gen_videos'); }
        document.getElementById('btnToAssembly').style.display = 'inline-flex';
      }
    } catch (e) { /* ignore polling errors */ }
  }, 5000));
}

// === Phase 4: Assembly (Step 5) ===
async function remixAssemble() {
  var btn = document.getElementById('btnAssemble');
  if (btn && btn.disabled) return; // prevent double-click
  if (btn) { btn.disabled = true; btn.textContent = rt('assembling'); }

  try {
    var resp = await fetch('/api/remix/assemble', { method: 'POST' });
    var data = await resp.json();
    if (!resp.ok || data.error) {
      alert(data.error || 'Assembly failed');
      if (btn) { btn.disabled = false; btn.textContent = rt('assemble_btn'); }
      return;
    }
    remixPollAssembly();
  } catch (err) {
    alert('Assembly failed: ' + err.message);
    if (btn) { btn.disabled = false; btn.textContent = rt('assemble_btn'); }
  }
}

function remixPollAssembly() {
  var interval = _remixRegisterInterval(setInterval(async function() {
    try {
      var resp = await fetch('/api/remix/status');
      var data = await resp.json();

      if (data.status === 'idle') { _remixClearInterval(interval); return; }

      var progressEl = document.getElementById('assemblyProgress');
      if (progressEl) {
        progressEl.innerHTML = '<div class="progress-bar"><div class="fill" style="width:' + data.progress + '%"></div></div>' +
          '<p class="status-text">' + escapeHtml(data.message || '') + '</p>';
      }

      if (data.status === 'done') {
        _remixClearInterval(interval);
        document.getElementById('assemblyProgress').style.display = 'none';
        var doneEl = document.getElementById('assemblyDone');
        doneEl.style.display = 'block';
        doneEl.innerHTML =
          '<div class="download-area">' +
          '<div class="icon">&#x2705;</div>' +
          '<p>' + escapeHtml(data.message || 'Video ready!') + '</p>' +
          '<a class="btn btn-primary" href="/api/remix/download" target="_blank">' + rt('download') + '</a>' +
          '<button class="btn btn-secondary" onclick="remixBurnSubtitles()" style="margin-left:8px;" id="btnBurnSubs">' + rt('goto_subtitles') + '</button>' +
          '<button class="btn btn-secondary" onclick="remixStartNew()" style="margin-left:8px;">' + rt('new_video') + '</button>' +
          '</div>';
        var btn = document.getElementById('btnAssemble');
        if (btn) btn.style.display = 'none';
      } else if (data.status === 'error') {
        _remixClearInterval(interval);
        alert(rt('task_fail') + data.message);
        var btn2 = document.getElementById('btnAssemble');
        if (btn2) { btn2.disabled = false; btn2.textContent = rt('assemble_btn'); }
      }
    } catch (e) { /* ignore polling errors */ }
  }, 2000));
}

// === Keyword Highlight + Burn Subtitles ===
let remixAutoKeywordMap = {};

function remixBurnSubtitles() {
  // Show keyword selection panel instead of immediately burning
  var doneEl = document.getElementById('assemblyDone');
  if (!doneEl) return;

  var chipLabels = {
    numbers: rt('kw_chip_numbers'), money: rt('kw_chip_money'), time: rt('kw_chip_time'),
    age: rt('kw_chip_age'), brand: rt('kw_chip_brand'), emotion: rt('kw_chip_emotion'),
  };
  var chips = '';
  for (var cat in chipLabels) {
    chips += '<span class="chip" data-cat="' + cat + '" onclick="this.classList.toggle(\'active\')">' + chipLabels[cat] + '</span>';
  }

  doneEl.innerHTML =
    '<div class="download-area">' +
    '<h3 style="margin:0 0 8px">' + rt('kw_title') + '</h3>' +
    '<p style="font-size:13px;color:#8e8e8e;margin-bottom:12px">' + rt('kw_desc') + '</p>' +
    '<div class="category-chips" id="remixCategoryChips">' + chips + '</div>' +
    '<div class="btn-group" style="margin-bottom:12px"><button class="btn btn-secondary" id="btnRemixAutoKw" onclick="remixAutoKeywords()">' + rt('kw_auto_detect') + '</button></div>' +
    '<div class="keyword-auto-results" id="remixKwAutoResults"></div>' +
    '<div class="divider"></div>' +
    '<label style="font-size:13px;color:#888;margin-bottom:6px;display:block">' + rt('kw_manual_label') + '</label>' +
    '<input class="keyword-input" id="remixKwInput" placeholder="' + escapeHtml(rt('kw_manual_placeholder')) + '">' +
    '<div class="btn-group" style="margin-bottom:16px"><button class="btn btn-secondary" id="btnRemixMatchKw" onclick="remixMatchKeywords()">' + rt('kw_match') + '</button></div>' +
    '<div class="keyword-matches" id="remixKwMatches"></div>' +
    '<div class="btn-group">' +
    '<button class="btn btn-secondary" onclick="remixConfirmBurn(false)">' + rt('kw_burn_skip') + '</button>' +
    '<button class="btn btn-primary" onclick="remixConfirmBurn(true)">' + rt('kw_burn') + '</button>' +
    '</div>' +
    '</div>';
}

async function remixAutoKeywords() {
  var chips = document.querySelectorAll('#remixCategoryChips .chip.active');
  var categories = Array.from(chips).map(function(c) { return c.dataset.cat; });
  if (categories.length === 0) { alert('Select at least one category'); return; }

  var btn = document.getElementById('btnRemixAutoKw');
  btn.disabled = true; btn.textContent = rt('kw_detecting');

  try {
    var resp = await fetch('/api/remix/keyword-categories', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({categories: categories}),
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    var data = await resp.json();
    if (data.error) throw new Error(data.error);
    remixAutoKeywordMap = data.matches || {};
    remixRenderAutoKeywords(remixAutoKeywordMap);
  } catch (err) {
    alert('Detection failed: ' + err.message);
  } finally {
    btn.disabled = false; btn.textContent = rt('kw_auto_detect');
  }
}

function remixRenderAutoKeywords(matches) {
  var container = document.getElementById('remixKwAutoResults');
  container.innerHTML = '';
  var chipLabels = {
    numbers: rt('kw_chip_numbers'), money: rt('kw_chip_money'), time: rt('kw_chip_time'),
    age: rt('kw_chip_age'), brand: rt('kw_chip_brand'), emotion: rt('kw_chip_emotion'),
  };
  for (var word in matches) {
    var cat = matches[word];
    var div = document.createElement('div');
    div.className = 'auto-keyword-item';
    div.innerHTML =
      '<input type="checkbox" data-word="' + escapeHtml(word) + '" checked>' +
      '<span class="auto-kw-word">' + escapeHtml(word) + '</span>' +
      '<span class="auto-kw-cat">' + (chipLabels[cat] || cat) + '</span>';
    container.appendChild(div);
  }
}

async function remixMatchKeywords() {
  var input = document.getElementById('remixKwInput').value.trim();
  if (!input) return;
  var keywords = input.split(/[,，]/).map(function(k) { return k.trim(); }).filter(Boolean);

  var btn = document.getElementById('btnRemixMatchKw');
  btn.disabled = true; btn.textContent = rt('kw_matching');

  try {
    var resp = await fetch('/api/remix/keywords', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({keywords: keywords}),
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    var data = await resp.json();
    if (data.error) throw new Error(data.error);
    remixRenderKeywordMatches(data.matches || {});
  } catch (err) {
    alert('Match failed: ' + err.message);
  } finally {
    btn.disabled = false; btn.textContent = rt('kw_match');
  }
}

function remixRenderKeywordMatches(matches) {
  var container = document.getElementById('remixKwMatches');
  container.innerHTML = '';
  for (var cn in matches) {
    var indo = matches[cn];
    var div = document.createElement('div');
    div.className = 'keyword-match';
    div.innerHTML =
      '<span class="cn">' + escapeHtml(cn) + '</span>' +
      '<span class="arrow">&#x2192;</span>' +
      '<input type="text" value="' + escapeHtml(indo || '') + '" data-cn="' + escapeHtml(cn) + '">';
    container.appendChild(div);
  }
}

function remixGetKeywordHighlights() {
  var highlights = {};
  // From auto-detected
  document.querySelectorAll('#remixKwAutoResults input[type="checkbox"]:checked').forEach(function(cb) {
    var word = cb.dataset.word;
    if (word) highlights[word] = true;
  });
  // From manual matches
  document.querySelectorAll('#remixKwMatches input').forEach(function(input) {
    var val = input.value.trim();
    if (val) highlights[val] = true;
  });
  return highlights;
}

async function remixConfirmBurn(withKeywords) {
  var keywords = withKeywords ? remixGetKeywordHighlights() : {};

  var doneEl = document.getElementById('assemblyDone');
  if (doneEl) {
    doneEl.innerHTML =
      '<div class="download-area">' +
      '<p>' + rt('generating') + '</p>' +
      '<div id="subtitleProgress"></div>' +
      '</div>';
  }

  try {
    var resp = await fetch('/api/remix/burn-subtitles', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({keywords: keywords}),
    });
    var data = await resp.json();
    if (!resp.ok || data.error) {
      alert(data.error || 'Subtitle burn failed');
      if (doneEl) {
        doneEl.innerHTML =
          '<div class="download-area">' +
          '<p style="color:#e74c3c;">' + escapeHtml(data.error || 'Error') + '</p>' +
          '<a class="btn btn-primary" href="/api/remix/download" target="_blank">' + rt('download') + '</a>' +
          '<button class="btn btn-secondary" onclick="remixBurnSubtitles()" style="margin-left:8px;" id="btnBurnSubs">' + rt('goto_subtitles') + '</button>' +
          '</div>';
      }
      return;
    }
    remixPollSubtitles();
  } catch (err) {
    alert('Subtitle burn failed: ' + err.message);
  }
}

function remixPollSubtitles() {
  var interval = _remixRegisterInterval(setInterval(async function() {
    try {
      var resp = await fetch('/api/remix/status');
      var data = await resp.json();

      if (data.status === 'idle') { _remixClearInterval(interval); return; }

      var doneEl = document.getElementById('assemblyDone');
      if (doneEl && data.status === 'subtitling') {
        var progressHtml = '<div class="progress-bar"><div class="fill" style="width:' + data.progress + '%"></div></div>' +
          '<p class="status-text">' + escapeHtml(data.message || '') + '</p>';
        var existingProgress = document.getElementById('subtitleProgress');
        if (!existingProgress) {
          doneEl.insertAdjacentHTML('beforeend', '<div id="subtitleProgress" style="margin-top:12px;">' + progressHtml + '</div>');
        } else {
          existingProgress.innerHTML = progressHtml;
        }
      }

      if (data.status === 'done') {
        _remixClearInterval(interval);
        doneEl.innerHTML =
          '<div class="download-area">' +
          '<div class="icon">&#x2705;</div>' +
          '<p>' + escapeHtml(data.message || 'Subtitles added!') + '</p>' +
          '<a class="btn btn-primary" href="/api/remix/download" target="_blank">' + rt('download') + '</a>' +
          '<button class="btn btn-secondary" onclick="remixStartNew()" style="margin-left:8px;">' + rt('new_video') + '</button>' +
          '</div>';
      } else if (data.status === 'error') {
        _remixClearInterval(interval);
        alert(rt('task_fail') + (data.message || 'Unknown error'));
        if (doneEl) {
          doneEl.innerHTML =
            '<div class="download-area">' +
            '<p style="color:#e74c3c;">' + escapeHtml(data.message || 'Error') + '</p>' +
            '<a class="btn btn-primary" href="/api/remix/download" target="_blank">' + rt('download') + '</a>' +
            '<button class="btn btn-secondary" onclick="remixBurnSubtitles()" style="margin-left:8px;">' + rt('goto_subtitles') + '</button>' +
            '</div>';
        }
      }
    } catch (e) {}
  }, 2000));
}

// === Per-segment translate ===
async function remixTranslateOne(idx) {
  var btn = document.getElementById('btnTransOne' + idx);
  if (btn) { btn.disabled = true; btn.textContent = '...'; }

  var textarea = document.querySelector('.script-textarea[data-idx="' + idx + '"]');
  var zhText = textarea ? textarea.value : remixSegments[idx].zh;

  if (!zhText || !zhText.trim()) {
    alert(rt('save_fail') + 'No text');
    if (btn) { btn.disabled = false; btn.textContent = rt('translate_one'); }
    return;
  }

  try {
    var resp = await fetch('/api/remix/translate-one', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idx: idx, zh: zhText }),
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    var data = await resp.json();
    if (data.error) throw new Error(data.error);

    remixSegments[idx].id = data.id;
    remixSegments[idx].id_word_count = data.word_count || 0;
    localStorage.setItem('remix_segments', JSON.stringify(remixSegments));
    renderScriptEditor();
  } catch (err) {
    alert(rt('translate_fail') + err.message);
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = rt('translate_one'); }
  }
}
