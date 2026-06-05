import os
import io
import base64
import time
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =============================================
# STATE MANAGEMENT — SEMUA DI MEMORI
# =============================================
image_state = {
    'original': None,       # numpy array — gambar asli (tidak pernah berubah)
    'current': None,        # numpy array — hasil edit terakhir
    'history': [],          # list of numpy array — untuk undo
    'filename': 'image.png' # nama file asli untuk download
}

def numpy_to_base64(img_array):
    """Konversi numpy array ke base64 string untuk dikirim ke browser"""
    if img_array is None:
        return None
    # Jika grayscale, konversi dulu ke BGR agar bisa diencode PNG
    if len(img_array.shape) == 2:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
    success, buffer = cv2.imencode('.png', img_array)
    if not success:
        return None
    b64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{b64}"

def push_history(img_array):
    """Simpan state saat ini ke history sebelum melakukan perubahan baru"""
    if img_array is not None:
        image_state['history'].append(img_array.copy())
        # Batasi history maksimal 20 langkah agar tidak makan RAM terlalu banyak
        if len(image_state['history']) > 20:
            image_state['history'].pop(0)

def generate_histogram_base64(img_array):
    """Buat histogram dari numpy array, return sebagai base64"""
    if img_array is None:
        return None
    if len(img_array.shape) == 2:
        img = img_array
    else:
        img = img_array

    plt.figure(figsize=(4, 2.5), facecolor='#17171a')
    ax = plt.axes()
    ax.set_facecolor('#1e1e22')
    ax.tick_params(colors='#9494a0', labelsize=8)

    if len(img.shape) == 2:
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        plt.plot(hist, color='#a8ff57', linewidth=1.5)
    else:
        hex_colors = ('#38bdf8', '#4ade80', '#ff5252')
        for i, hc in enumerate(hex_colors):
            hist = cv2.calcHist([img], [i], None, [256], [0, 256])
            plt.plot(hist, color=hc, linewidth=1.5)

    plt.xlim([0, 256])
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{b64}"

# =============================================
# ROUTES
# =============================================

@app.route('/')
def index():
    original_b64  = numpy_to_base64(image_state['original'])
    current_b64   = numpy_to_base64(image_state['current'])
    hist_ori_b64  = generate_histogram_base64(image_state['original'])
    hist_proc_b64 = generate_histogram_base64(image_state['current'])
    can_undo      = len(image_state['history']) > 0

    return render_template('index.html',
                           original_image=original_b64,
                           processed_image=current_b64,
                           hist_original=hist_ori_b64,
                           hist_processed=hist_proc_b64,
                           can_undo=can_undo,
                           filename=image_state['filename'])

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(url_for('index'))
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('index'))

    # Baca langsung ke numpy array — tidak disimpan ke disk
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is not None:
        image_state['original'] = img.copy()
        image_state['current']  = img.copy()
        image_state['history']  = []
        image_state['filename'] = file.filename or 'image.png'

    return redirect(url_for('index'))

@app.route('/load_sample')
def load_sample():
    color = request.args.get('color', 'green')
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    if color == 'green':
        img[:] = (0, 200, 0)
    elif color == 'purple':
        img[:] = (200, 0, 150)
    elif color == 'blue':
        img[:] = (255, 100, 0)

    image_state['original'] = img.copy()
    image_state['current']  = img.copy()
    image_state['history']  = []
    image_state['filename'] = f"sample_{color}.png"
    return redirect(url_for('index'))

@app.route('/reset')
def reset_image():
    image_state['original'] = None
    image_state['current']  = None
    image_state['history']  = []
    image_state['filename'] = 'image.png'
    return redirect(url_for('index'))

@app.route('/download')
def download_image():
    """Encode gambar current ke bytes lalu kirim sebagai file download"""
    if image_state['current'] is None:
        return redirect(url_for('index'))

    img = image_state['current']
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    success, buffer = cv2.imencode('.png', img)
    if not success:
        return redirect(url_for('index'))

    return send_file(
        io.BytesIO(buffer.tobytes()),
        mimetype='image/png',
        as_attachment=True,
        download_name=f"photolab_{image_state['filename']}"
    )

# =============================================
# API — UNDO
# =============================================

@app.route('/api/undo', methods=['POST'])
def undo():
    if len(image_state['history']) == 0:
        return jsonify({'error': 'Tidak ada yang bisa di-undo'}), 400

    image_state['current'] = image_state['history'].pop()
    current_b64  = numpy_to_base64(image_state['current'])
    hist_b64     = generate_histogram_base64(image_state['current'])
    can_undo     = len(image_state['history']) > 0

    return jsonify({
        'processed_image': current_b64,
        'hist_proc': hist_b64,
        'can_undo': can_undo
    })

# =============================================
# API — PROSES GAMBAR (STACKING)
# =============================================

@app.route('/api/process', methods=['POST'])
def process_image_api():
    if image_state['current'] is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data   = request.json
    action = data.get('action')
    params = data.get('params', {})

    # Baca dari STATE TERAKHIR (bukan original) — ini yang membuat efek stack
    img = image_state['current'].copy()

    # Jika gambar grayscale (2D), konversi ke BGR untuk proses yang butuh warna
    if len(img.shape) == 2:
        img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    else:
        img_bgr = img

    out_img = img_bgr.copy()

    # ---- PROSES ----

    if action == 'grayscale':
        out_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    elif action == 'histogram_equalization':
        ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
        out_img = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    elif action == 'brightness_contrast':
        b_val = int(params.get('brightness', 0))
        c_val = float(params.get('contrast', 1.0))
        out_img = cv2.convertScaleAbs(img_bgr, alpha=c_val, beta=b_val)

    elif action == 'saturation':
        value = float(params.get('value', 1.0))
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * value, 0, 255)
        out_img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    elif action == 'hue_rotate':
        angle = int(params.get('angle', 0))
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.int32)
        hsv[:, :, 0] = (hsv[:, :, 0] + angle) % 180
        out_img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    elif action == 'color_channel':
        channel = params.get('channel', 'R')
        b, g, r = cv2.split(img_bgr)
        blank = np.zeros_like(b)
        if channel == 'R':
            out_img = cv2.merge([blank, blank, r])
        elif channel == 'G':
            out_img = cv2.merge([blank, g, blank])
        elif channel == 'B':
            out_img = cv2.merge([b, blank, blank])

    elif action == 'sharpening':
        kernel  = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        out_img = cv2.filter2D(img_bgr, -1, kernel)

    elif action == 'blur_filter':
        filter_type = params.get('type', 'gaussian')
        k_size = int(params.get('kernel', 5))
        if k_size % 2 == 0:
            k_size += 1
        if filter_type == 'gaussian':
            out_img = cv2.GaussianBlur(img_bgr, (k_size, k_size), 0)
        elif filter_type == 'median':
            out_img = cv2.medianBlur(img_bgr, k_size)

    elif action == 'rotate':
        angle = int(params.get('angle', 0))
        h, w  = img_bgr.shape[:2]
        M     = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        out_img = cv2.warpAffine(img_bgr, M, (w, h))

    elif action == 'flip':
        direction  = params.get('direction', 'horizontal')
        flip_code  = 1 if direction == 'horizontal' else 0
        out_img    = cv2.flip(img_bgr, flip_code)

    elif action == 'resize':
        scale   = float(params.get('scale', 100)) / 100.0
        out_img = cv2.resize(img_bgr, None, fx=scale, fy=scale,
                             interpolation=cv2.INTER_LINEAR)

    elif action == 'crop_center':
        h, w   = img_bgr.shape[:2]
        cy, cx = h // 2, w // 2
        half   = min(cy, cx)
        out_img = img_bgr[cy - half:cy + half, cx - half:cx + half]

    elif action == 'crop_manual':
        x = int(params.get('x', 0))
        y = int(params.get('y', 0))
        w = int(params.get('w', img_bgr.shape[1]))
        h = int(params.get('h', img_bgr.shape[0]))
        x = max(0, x)
        y = max(0, y)
        w = min(w, img_bgr.shape[1] - x)
        h = min(h, img_bgr.shape[0] - y)
        out_img = img_bgr[y:y + h, x:x + w] if w > 0 and h > 0 else img_bgr.copy()

    elif action == 'add_text':
        text      = params.get('text', 'Teks')
        if not text.strip():
            text = 'Teks'
        size      = float(params.get('size', 32))
        x         = int(params.get('x', 20))
        y         = int(params.get('y', 50))
        color_hex = params.get('color', '#ffffff').lstrip('#')
        try:
            r2 = int(color_hex[0:2], 16)
            g2 = int(color_hex[2:4], 16)
            b2 = int(color_hex[4:6], 16)
        except Exception:
            r2, g2, b2 = 255, 255, 255
        bgr_color  = (b2, g2, r2)
        font_scale = size / 20.0
        thickness  = max(1, int(font_scale * 2))
        out_img    = img_bgr.copy()
        cv2.putText(out_img, text, (x + 2, y + 2),
                    cv2.FONT_HERSHEY_DUPLEX, font_scale,
                    (0, 0, 0), thickness + 2, cv2.LINE_AA)
        cv2.putText(out_img, text, (x, y),
                    cv2.FONT_HERSHEY_DUPLEX, font_scale,
                    bgr_color, thickness, cv2.LINE_AA)

    elif action == 'edge_detection':
        method = params.get('method', 'canny')
        gray   = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        if method == 'canny':
            out_img = cv2.Canny(gray, 50, 150)
        elif method == 'sobel':
            sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            out_img = cv2.convertScaleAbs(np.sqrt(sx ** 2 + sy ** 2))
        elif method == 'laplacian':
            out_img = cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_64F))
        elif method == 'prewitt':
            gray   = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            kx     = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=np.float32)
            ky     = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32)
            px     = cv2.filter2D(gray, -1, kx)
            py     = cv2.filter2D(gray, -1, ky)
            out_img = cv2.convertScaleAbs(np.sqrt(px.astype(np.float32)**2 + py.astype(np.float32)**2))

    elif action == 'morphology':
        m_type = params.get('type', 'erosion')
        k_size = int(params.get('kernel', 3))
        gray   = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        kernel = np.ones((k_size, k_size), np.uint8)
        if m_type == 'erosion':
            out_img = cv2.erode(thresh, kernel, iterations=1)
        elif m_type == 'dilation':
            out_img = cv2.dilate(thresh, kernel, iterations=1)

    elif action == 'cnn_detect':
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        out_img = img_bgr.copy()
        for c in contours:
            if cv2.contourArea(c) > 500:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(out_img, (x, y), (x + w, y + h), (87, 255, 168), 2)
                cv2.putText(out_img, "Objek", (x, y - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (87, 255, 168), 1)

    else:
        return jsonify({'error': f'Action tidak dikenal: {action}'}), 400

    # ---- SIMPAN KE HISTORY & UPDATE STATE ----
    push_history(image_state['current'])
    image_state['current'] = out_img

    # ---- ENCODE KE BASE64 & KIRIM ----
    current_b64  = numpy_to_base64(out_img)
    hist_b64     = generate_histogram_base64(out_img)
    can_undo     = len(image_state['history']) > 0

    return jsonify({
        'processed_image': current_b64,
        'hist_proc': hist_b64,
        'can_undo': can_undo
    })

if __name__ == '__main__':
    app.run(debug=True)