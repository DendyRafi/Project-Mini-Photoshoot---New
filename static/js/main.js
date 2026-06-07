// =============================================
// TOOL CARD — event delegation
// =============================================
document.addEventListener('click', function(e) {
    const card = e.target.closest('.tool-card[data-action]');
    if (card) {
        const action = card.getAttribute('data-action');
        if (action) eval(action);
    }
});

// =============================================
// TAB SWITCHING
// =============================================
let activeTabId = 'tab-dasar';

document.querySelectorAll('.rail-btn[data-tab]').forEach(btn => {
    btn.addEventListener('click', e => {
        e.preventDefault();
        clearSearch();
        switchTab(btn.dataset.tab);
        // Di mobile: buka panel saat klik rail btn
        if (isMobile()) {
            const panel   = document.querySelector('.tools-panel');
            const overlay = document.getElementById('mobileOverlay');
            if (panel && overlay) {
                panel.classList.add('mobile-open');
                overlay.classList.add('active');
            }
        }
    });
});

function switchTab(tabId) {
    activeTabId = tabId;
    document.getElementById('search-results').style.display = 'none';
    document.getElementById('search-input').value = '';
    document.querySelectorAll('.rail-btn').forEach(b => b.classList.remove('active'));
    const activeBtn = document.querySelector(`.rail-btn[data-tab="${tabId}"]`);
    if (activeBtn) activeBtn.classList.add('active');
    document.querySelectorAll('.tab-content').forEach(t => {
        if (t.id === 'search-results') return;
        t.classList.remove('active');
        t.style.display = 'none';
    });
    const activeTab = document.getElementById(tabId);
    if (activeTab) {
        activeTab.classList.add('active');
        activeTab.style.display = 'block';
    }
}

// =============================================
// SEARCH BAR
// =============================================
document.getElementById('search-input').addEventListener('input', function() {
    const query = this.value.toLowerCase().trim();
    if (!query) { clearSearch(); return; }

    document.querySelectorAll('.tab-content').forEach(t => {
        if (t.id !== 'search-results') t.style.display = 'none';
    });

    const allFeatures = [
        { label: 'Grayscale',                   action: "applyFilter('grayscale')" },
        { label: 'Gaussian Blur / Smoothing',    action: "applyFilter('blur_filter',{type:'gaussian',kernel:9})" },
        { label: 'Median Filter',                action: "applyFilter('blur_filter',{type:'median',kernel:5})" },
        { label: 'Sharpening',                   action: "applyFilter('sharpening')" },
        { label: 'Canny Edge',                   action: "applyFilter('edge_detection',{method:'canny'})" },
        { label: 'Sobel Edge',                   action: "applyFilter('edge_detection',{method:'sobel'})" },
        { label: 'Prewitt Edge',                 action: "applyFilter('edge_detection',{method:'prewitt'})" },
        { label: 'Robert Edge',                  action: "applyFilter('edge_robert')" },
        { label: 'Laplacian',                    action: "applyFilter('edge_detection',{method:'laplacian'})" },
        { label: 'Laplacian of Gaussian LoG',    action: "applyFilter('edge_log')" },
        { label: 'Brightness',                   action: "switchTab('tab-adjust')" },
        { label: 'Contrast',                     action: "switchTab('tab-adjust')" },
        { label: 'Saturation',                   action: "switchTab('tab-adjust')" },
        { label: 'Hue Rotate',                   action: "switchTab('tab-adjust')" },
        { label: 'Histogram Equalization',        action: "applyFilter('histogram_equalization')" },
        { label: 'Salt Pepper Noise',            action: "applyFilter('noise_saltpepper',{amount:0.02})" },
        { label: 'Noise Removal',                action: "applyFilter('noise_removal_sp',{kernel:3})" },
        { label: 'Threshold Thresholding',       action: "switchTab('tab-edge')" },
        { label: 'Erosi Erosion',                action: "applyFilter('morphology',{type:'erosion',kernel:3})" },
        { label: 'Dilatasi Dilation',            action: "applyFilter('morphology',{type:'dilation',kernel:3})" },
        { label: 'Crop',                         action: "switchTab('tab-transform')" },
        { label: 'Rotate Rotasi',                action: "switchTab('tab-transform')" },
        { label: 'Flip Horizontal',              action: "applyFilter('flip',{direction:'horizontal'})" },
        { label: 'Flip Vertical',                action: "applyFilter('flip',{direction:'vertical'})" },
        { label: 'Resize Skala',                 action: "switchTab('tab-transform')" },
        { label: 'Translation Geser',            action: "switchTab('tab-transform')" },
        { label: 'Interpolasi',                  action: "switchTab('tab-transform')" },
        { label: 'Red Channel',                  action: "applyFilter('color_channel',{channel:'R'})" },
        { label: 'Green Channel',                action: "applyFilter('color_channel',{channel:'G'})" },
        { label: 'Blue Channel',                 action: "applyFilter('color_channel',{channel:'B'})" },
        { label: 'Segmentasi Threshold',         action: "switchTab('tab-segmentasi')" },
        { label: 'Segmentasi Edge Kontur',       action: "applyFilter('segmentation_edge')" },
        { label: 'Segmentasi Region Watershed',  action: "applyFilter('segmentation_region')" },
        { label: 'Kompresi RLE',                 action: "applyFilter('compress_rle')" },
        { label: 'Kompresi JPEG',                action: "switchTab('tab-segmentasi')" },
        { label: 'Tambah Teks',                  action: "switchTab('tab-text')" },
        { label: 'Histogram',                    action: "switchTab('tab-histogram')" },
    ];

    const matched = allFeatures.filter(f => f.label.toLowerCase().includes(query));
    const panel   = document.getElementById('search-results');
    panel.innerHTML = `<p class="section-label">Hasil Pencarian</p>`;

    if (matched.length === 0) {
        panel.innerHTML += `<p style="font-size:12px;color:var(--text-3);padding:4px 0;">Tidak ada hasil untuk "<b>${query}</b>"</p>`;
    } else {
        const list = document.createElement('div');
        list.style.cssText = 'display:flex;flex-direction:column;gap:6px;';
        matched.forEach(f => {
            const btn = document.createElement('button');
            btn.className    = 'btn-apply';
            btn.style.marginTop = '0';
            btn.textContent  = f.label;
            btn.title        = f.label;
            btn.addEventListener('click', () => { clearSearch(); eval(f.action); });
            list.appendChild(btn);
        });
        panel.appendChild(list);
    }
    panel.style.display = 'block';
});

function clearSearch() {
    document.getElementById('search-input').value = '';
    document.getElementById('search-results').style.display = 'none';
    document.querySelectorAll('.tab-content').forEach(t => {
        if (t.id === 'search-results') return;
        t.style.display = 'none';
        t.classList.remove('active');
    });
    const activeTab = document.getElementById(activeTabId);
    if (activeTab) { activeTab.style.display = 'block'; activeTab.classList.add('active'); }
    document.querySelectorAll('.rail-btn').forEach(b => b.classList.remove('active'));
    const activeBtn = document.querySelector(`.rail-btn[data-tab="${activeTabId}"]`);
    if (activeBtn) activeBtn.classList.add('active');
}

// =============================================
// AJAX FILTER
// =============================================
function applyFilter(actionName, parameterObject = {}) {
    setStatus('processing');
    fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionName, params: parameterObject })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) { setStatus('error', data.error); return; }
        updateProcessed(data.processed_image);
        if (data.hist_proc) {
            const hp = document.getElementById('img-hist-proc');
            if (hp) hp.src = data.hist_proc;
        }
        updateUndoBtn(data.can_undo);
        setStatus('done');
    })
    .catch(err => { setStatus('error', 'Koneksi error'); console.error(err); });
}

function applyFilterPreview(actionName, parameterObject = {}) {
    setStatus('processing');
    parameterObject._preview = true;
    fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionName, params: parameterObject })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) { setStatus('error', data.error); return; }
        updateProcessed(data.processed_image);
        setStatus('done');
    })
    .catch(err => { setStatus('error', 'Koneksi error'); console.error(err); });
}

function updateProcessed(src) {
    const img = document.getElementById('display-processed');
    if (img && src) img.src = src;
}

function setStatus(state, msg) {
    const el = document.getElementById('status-loading');
    if (!el) return;
    el.className = 'zoom-info';
    if (state === 'processing') { el.classList.add('status-processing'); el.textContent = 'Memproses...'; }
    else if (state === 'done')  { el.classList.add('status-done');       el.textContent = 'Selesai ✓'; }
    else if (state === 'error') { el.classList.add('status-error');      el.textContent = msg || 'Error!'; }
}

// =============================================
// BEGIN ADJUST — simpan snapshot sebelum slider
// =============================================
let adjustStarted = false;

function beginAdjust() {
    if (adjustStarted) return; // cegah dipanggil berkali-kali
    adjustStarted = true;
    fetch('/api/begin_adjust', { method: 'POST' })
    .catch(err => console.error('begin_adjust error:', err));
}

// Reset flag saat mouse dilepas dari slider mana pun
document.addEventListener('mouseup',  () => { adjustStarted = false; });
document.addEventListener('touchend', () => { adjustStarted = false; });

// =============================================
// COMMIT ADJUST — terapkan slider ke history
// =============================================
function commitAdjust(type) {
    if (type === 'brightness_contrast') {
        const b = document.getElementById('range-brightness').value;
        const c = document.getElementById('range-contrast').value / 10;
        applyFilter('brightness_contrast', { brightness: b, contrast: c });
    } else if (type === 'saturation') {
        const v = document.getElementById('range-saturation').value / 10;
        applyFilter('saturation', { value: v });
    } else if (type === 'hue_rotate') {
        const a = document.getElementById('range-hue').value;
        applyFilter('hue_rotate', { angle: a });
    }
}

// =============================================
// UNDO & RESET
// =============================================
function updateUndoBtn(canUndo) {
    const btn = document.getElementById('undo-btn');
    if (!btn) return;
    if (canUndo) btn.classList.add('has-history');
    else btn.classList.remove('has-history');
}

function doUndo() {
    setStatus('processing');
    fetch('/api/undo', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
        if (data.error) { setStatus('error', data.error); return; }
        updateProcessed(data.processed_image);
        if (data.hist_proc) {
            const hp = document.getElementById('img-hist-proc');
            if (hp) hp.src = data.hist_proc;
        }
        updateUndoBtn(data.can_undo);
        setStatus('done');
    })
    .catch(err => { setStatus('error', 'Koneksi error'); console.error(err); });
}

function doResetToOriginal() {
    if (!confirm('Kembalikan ke gambar awal? Semua edit akan hilang.')) return;
    setStatus('processing');
    fetch('/api/reset_to_original', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
        if (data.error) { setStatus('error', data.error); return; }
        updateProcessed(data.processed_image);
        if (data.hist_proc) {
            const hp = document.getElementById('img-hist-proc');
            if (hp) hp.src = data.hist_proc;
        }
        updateUndoBtn(false);
        document.getElementById('status-loading').textContent = 'Dikembalikan ke gambar awal ✓';
    })
    .catch(err => { setStatus('error', 'Koneksi error'); console.error(err); });
}

function updateDownloadLink() {
    const fmt       = document.getElementById('select-format');
    const nameInput = document.getElementById('input-filename');
    const link      = document.getElementById('btn-download-link');
    if (!fmt || !link) return;
    const filename = (nameInput && nameInput.value.trim()) ? nameInput.value.trim() : 'hasil-edit';
    link.href = '/download?format=' + fmt.value + '&filename=' + encodeURIComponent(filename);
}

// =============================================
// BRIGHTNESS & CONTRAST
// =============================================
function updateSliderVal(slider) {
    if (slider.id === 'range-brightness')
        document.getElementById('val-brightness').textContent = slider.value;
    if (slider.id === 'range-contrast')
        document.getElementById('val-contrast').textContent = (slider.value / 10).toFixed(1);
}

// Dipanggil saat slider dilepas — preview dari adjustment_base
function commitSlider(type) {
    adjustStarted = false;
    if (type === 'brightness_contrast') {
        const b = document.getElementById('range-brightness').value;
        const c = document.getElementById('range-contrast').value / 10;
        applyFilterPreview('brightness_contrast', { brightness: b, contrast: c });
    } else if (type === 'saturation') {
        const v = document.getElementById('range-saturation').value / 10;
        applyFilterPreview('saturation', { value: v });
    } else if (type === 'hue_rotate') {
        const a = document.getElementById('range-hue').value;
        applyFilterPreview('hue_rotate', { angle: a });
    }
}

// Dipanggil tombol Terapkan — commit ke history
function commitAdjust(type) {
    if (type === 'brightness_contrast') {
        const b = document.getElementById('range-brightness').value;
        const c = document.getElementById('range-contrast').value / 10;
        applyFilter('brightness_contrast', { brightness: b, contrast: c });
    } else if (type === 'saturation') {
        const v = document.getElementById('range-saturation').value / 10;
        applyFilter('saturation', { value: v });
    } else if (type === 'hue_rotate') {
        const a = document.getElementById('range-hue').value;
        applyFilter('hue_rotate', { angle: a });
    }
}

// =============================================
// CROP — DRAG TO SELECT
// =============================================
let cropMode  = false;
let cropStart = null;
let cropRect  = {};

function startCropMode() {
    const overlay = document.getElementById('crop-overlay');
    if (!overlay) { alert('Upload gambar dulu!'); return; }
    cancelTextMode();
    cropMode  = true;
    cropStart = null;
    cropRect  = {};
    const sel     = document.getElementById('crop-selection');
    const toolbar = document.getElementById('crop-toolbar');
    overlay.classList.add('active');
    sel.style.display = 'none';
    toolbar.classList.remove('visible');
    document.getElementById('status-loading').textContent = 'Mode Crop — Drag pada gambar';
    overlay.onmousedown = onCropMouseDown;
    overlay.onmousemove = onCropMouseMove;
    overlay.onmouseup   = onCropMouseUp;
}

function onCropMouseDown(e) {
    e.preventDefault();
    const overlay = document.getElementById('crop-overlay');
    const rect    = overlay.getBoundingClientRect();
    cropStart = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    const sel = document.getElementById('crop-selection');
    sel.style.display = 'block';
    sel.style.left    = cropStart.x + 'px';
    sel.style.top     = cropStart.y + 'px';
    sel.style.width   = '0px';
    sel.style.height  = '0px';
}

function onCropMouseMove(e) {
    if (!cropStart) return;
    e.preventDefault();
    const overlay = document.getElementById('crop-overlay');
    const rect    = overlay.getBoundingClientRect();
    const cx = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const cy = Math.max(0, Math.min(e.clientY - rect.top,  rect.height));
    const x  = Math.min(cropStart.x, cx);
    const y  = Math.min(cropStart.y, cy);
    const w  = Math.abs(cx - cropStart.x);
    const h  = Math.abs(cy - cropStart.y);
    const sel = document.getElementById('crop-selection');
    sel.style.left   = x + 'px';
    sel.style.top    = y + 'px';
    sel.style.width  = w + 'px';
    sel.style.height = h + 'px';
    cropRect = { x, y, w, h };
}

function onCropMouseUp() {
    if (!cropStart) return;
    cropStart = null;
    if (cropRect.w > 5 && cropRect.h > 5)
        document.getElementById('crop-toolbar').classList.add('visible');
}

function confirmCrop() {
    if (!cropRect.w || !cropRect.h) return;
    const img     = document.getElementById('display-processed');
    const imgRect = img.getBoundingClientRect();
    const overlay = document.getElementById('crop-overlay');
    const ovRect  = overlay.getBoundingClientRect();
    const imgOffX = imgRect.left - ovRect.left;
    const imgOffY = imgRect.top  - ovRect.top;
    const relX    = cropRect.x - imgOffX;
    const relY    = cropRect.y - imgOffY;
    const scaleX  = img.naturalWidth  / imgRect.width;
    const scaleY  = img.naturalHeight / imgRect.height;
    const realX   = Math.max(0, Math.round(relX * scaleX));
    const realY   = Math.max(0, Math.round(relY * scaleY));
    const realW   = Math.min(Math.round(cropRect.w * scaleX), img.naturalWidth  - realX);
    const realH   = Math.min(Math.round(cropRect.h * scaleY), img.naturalHeight - realY);
    cancelCrop();
    applyFilter('crop_manual', { x: realX, y: realY, w: realW, h: realH });
}

function cancelCrop() {
    cropMode  = false;
    cropStart = null;
    cropRect  = {};
    const overlay = document.getElementById('crop-overlay');
    const sel     = document.getElementById('crop-selection');
    const toolbar = document.getElementById('crop-toolbar');
    if (overlay) {
        overlay.classList.remove('active');
        overlay.onmousedown = null;
        overlay.onmousemove = null;
        overlay.onmouseup   = null;
    }
    if (sel)     sel.style.display = 'none';
    if (toolbar) toolbar.classList.remove('visible');
    const st = document.getElementById('status-loading');
    if (st) st.textContent = 'Siap diproses';
}

// =============================================
// TEXT — CLICK TO PLACE
// =============================================
let textMode = false;

function startTextMode() {
    const text = document.getElementById('input-text').value.trim();
    if (!text) { alert('Isi teks dulu!'); document.getElementById('input-text').focus(); return; }
    cancelCrop();
    textMode = true;
    const overlay = document.getElementById('text-overlay');
    if (!overlay) return;
    overlay.classList.add('active');
    document.getElementById('btn-text-mode').style.display   = 'none';
    document.getElementById('btn-text-cancel').style.display = 'block';
    document.getElementById('status-loading').textContent    = 'Mode Teks — Klik posisi pada gambar';
    updateTextPreview();
    overlay.onmousemove = onTextMouseMove;
    overlay.onclick     = onTextClick;
}

function stopTextMode() {
    textMode = false;
    const overlay = document.getElementById('text-overlay');
    const preview = document.getElementById('text-preview');
    if (overlay) { overlay.classList.remove('active'); overlay.onmousemove = null; overlay.onclick = null; }
    if (preview) preview.style.display = 'none';
    document.getElementById('btn-text-mode').style.display   = 'block';
    document.getElementById('btn-text-cancel').style.display = 'none';
    const st = document.getElementById('status-loading');
    if (st) st.textContent = 'Siap diproses';
}

function cancelTextMode() { if (textMode) stopTextMode(); }

function updateTextPreview() {
    const preview = document.getElementById('text-preview');
    if (!preview) return;
    const text  = document.getElementById('input-text')      ? document.getElementById('input-text').value || 'Teks'  : 'Teks';
    const size  = document.getElementById('range-fontsize')  ? document.getElementById('range-fontsize').value        : 32;
    const color = document.getElementById('input-textcolor') ? document.getElementById('input-textcolor').value       : '#ffffff';
    preview.textContent    = text;
    preview.style.fontSize = size + 'px';
    preview.style.color    = color;
}

function onTextMouseMove(e) {
    const preview = document.getElementById('text-preview');
    const overlay = document.getElementById('text-overlay');
    if (!preview || !overlay) return;
    const rect = overlay.getBoundingClientRect();
    preview.style.display = 'block';
    preview.style.left    = (e.clientX - rect.left) + 'px';
    preview.style.top     = (e.clientY - rect.top)  + 'px';
}

function onTextClick(e) {
    const img     = document.getElementById('display-processed');
    const overlay = document.getElementById('text-overlay');
    if (!img || !overlay) return;
    const imgRect = img.getBoundingClientRect();
    const ox      = e.clientX - imgRect.left;
    const oy      = e.clientY - imgRect.top;
    if (ox < 0 || oy < 0 || ox > imgRect.width || oy > imgRect.height) return;
    const scaleX  = img.naturalWidth  / imgRect.width;
    const scaleY  = img.naturalHeight / imgRect.height;
    const realX   = Math.round(ox * scaleX);
    const realY   = Math.round(oy * scaleY);
    const text    = document.getElementById('input-text').value.trim() || 'Teks';
    const size    = parseInt(document.getElementById('range-fontsize').value) || 32;
    const color   = document.getElementById('input-textcolor').value || '#ffffff';
    stopTextMode();
    applyFilter('add_text', { text, size, x: realX, y: realY, color });
}

// Update semua label slider saat halaman pertama load
document.addEventListener('DOMContentLoaded', function() {
    const brightness = document.getElementById('range-brightness');
    const contrast   = document.getElementById('range-contrast');
    const saturation = document.getElementById('range-saturation');
    const hue        = document.getElementById('range-hue');
    if (brightness) document.getElementById('val-brightness').textContent = brightness.value;
    if (contrast)   document.getElementById('val-contrast').textContent   = (contrast.value / 10).toFixed(1);
    if (saturation) document.getElementById('val-saturation').textContent = (saturation.value / 10).toFixed(1);
    if (hue)        document.getElementById('val-hue').textContent        = hue.value + '°';
});

document.addEventListener("DOMContentLoaded", () => {
    // Targetkan class brand-name yang baru kita beri penanda glitch
    const logo = document.querySelector(".brand-name.glitch-logo");

    if (logo) {
        function triggerGlitch() {
            // Aktifkan glitch
            logo.classList.add("is-glitching");

            // Matikan glitch setelah 350ms agar kedipannya cepat dan natural
            setTimeout(() => {
                logo.classList.remove("is-glitching");
            }, 350);

            // Pengulangan acak antara 3 sampai 6 detik sekali
            const randomDelay = Math.random() * (1000 - 500) + 3000;
            setTimeout(triggerGlitch, randomDelay);
        }

        // Jalankan efek pertama kali setelah web di-load
        setTimeout(triggerGlitch, 1500);
    }
});

// =============================================
// MOBILE PANEL TOGGLE
// =============================================
function isMobile() { return window.innerWidth <= 768; }

function toggleMobilePanel() {
    const panel   = document.querySelector('.tools-panel');
    const overlay = document.getElementById('mobileOverlay');
    if (!panel || !overlay) return;
    panel.classList.toggle('mobile-open');
    overlay.classList.toggle('active');
}

function closeMobilePanel() {
    const panel   = document.querySelector('.tools-panel');
    const overlay = document.getElementById('mobileOverlay');
    if (!panel || !overlay) return;
    panel.classList.remove('mobile-open');
    overlay.classList.remove('active');
}

function checkMobileLayout() {
    const btn = document.querySelector('.mobile-menu-btn');
    if (!btn) return;
    btn.style.display = isMobile() ? 'flex' : 'none';
}

// Override switchTab agar di mobile otomatis buka panel dulu
const _origSwitchTab = switchTab;
switchTab = function(tabId) {
    _origSwitchTab(tabId);
    if (isMobile()) {
        const panel   = document.querySelector('.tools-panel');
        const overlay = document.getElementById('mobileOverlay');
        if (panel && overlay) {
            panel.classList.add('mobile-open');
            overlay.classList.add('active');
        }
    }
};

window.addEventListener('resize', checkMobileLayout);

// Jalankan setelah DOM benar-benar siap
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkMobileLayout);
} else {
    checkMobileLayout();
}