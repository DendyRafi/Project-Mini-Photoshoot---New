import os, io, base64, cv2, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify

from processing.color       import apply_grayscale, apply_color_channel, apply_saturation, apply_hue_rotate
from processing.enhance     import apply_brightness_contrast, apply_histogram_equalization
from processing.filter      import apply_blur, apply_sharpening, apply_noise_saltpepper, apply_noise_removal
from processing.edge        import apply_edge_detection, apply_edge_robert, apply_edge_log
from processing.transform   import apply_rotate, apply_flip, apply_resize, apply_crop_center, apply_crop_manual, apply_translation, apply_interpolation
from processing.morphology  import apply_morphology, apply_threshold
from processing.segmentation import apply_segmentation_threshold, apply_segmentation_edge, apply_segmentation_region
from processing.compression  import apply_compress_jpeg, apply_compress_rle

app = Flask(__name__)

# =========================================================================
# 1. TAMBAHAN: MEMBUAT FOLDER STORAGE OTOMATIS DI SERVER RENDER
# =========================================================================
# Ini mencegah aplikasi crash (Error Status 1) akibat folder kosong yang 
# tidak terbawa dari GitHub ke server cloud.
UPLOAD_FOLDER = os.path.join('static', 'uploads')
OUTPUT_FOLDER = os.path.join('static', 'outputs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# =========================================================================

image_state = {
    'original':         None,
    'current':          None,
    'history':          [],
    'filename':         'image.png',
    'adjustment_base':  None,
    'original_dims':    None,  # Track original dimensions untuk validasi crop
    'before_channel_view': None,  # State sebelum pilih color_channel (untuk recovery)
}

VALID_ACTIONS = {
    'grayscale', 'histogram_equalization', 'brightness_contrast',
    'saturation', 'hue_rotate', 'color_channel', 'sharpening',
    'blur_filter', 'rotate', 'flip', 'resize', 'crop_center',
    'crop_manual', 'add_text', 'edge_detection', 'edge_robert',
    'edge_log', 'morphology', 'compress', 'compress_rle',
    'translation', 'noise_saltpepper', 'noise_removal_sp', 
    'threshold', 'segmentation_threshold', 'segmentation_edge', 
    'segmentation_region', 'interpolation'
}

# =============================================
# HELPER FUNCTIONS
# =============================================

def numpy_to_base64(img_array):
    """Convert numpy array ke base64 PNG string."""
    if img_array is None:
        return None
    if len(img_array.shape) == 2:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
    success, buffer = cv2.imencode('.png', img_array)
    if not success:
        return None
    b64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{b64}"

def push_history(img_array):
    """Simpan snapshot ke history (max 20 items)."""
    if img_array is not None and img_array.size > 0:
        image_state['history'].append(img_array.copy())
        if len(image_state['history']) > 20:
            image_state['history'].pop(0)

def generate_histogram_base64(img_array):
    """Generate histogram visualization sebagai base64 PNG."""
    if img_array is None:
        return None
    try:
        plt.figure(figsize=(4, 2.5), facecolor='#17171a')
        ax = plt.axes()
        ax.set_facecolor('#1e1e22')
        ax.tick_params(colors='#9494a0', labelsize=8)
        if len(img_array.shape) == 2:
            hist = cv2.calcHist([img_array], [0], None, [256], [0, 256])
            plt.plot(hist, color='#a8ff57', linewidth=1.5)
        else:
            hex_colors = ('#38bdf8', '#4ade80', '#ff5252')
            for i, hc in enumerate(hex_colors):
                hist = cv2.calcHist([img_array], [i], None, [256], [0, 256])
                plt.plot(hist, color=hc, linewidth=1.5)
        plt.xlim([0, 256])
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{b64}"
    except Exception:
        plt.close()
        return None

def ensure_bgr(img):
    """Pastikan gambar adalah 3-channel BGR."""
    if img is None:
        return None
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.shape[2] == 1:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img

def is_valid_image(img):
    """Check apakah image valid dan bukan kosong."""
    return img is not None and len(img.shape) >= 2 and img.size > 0

def is_single_channel_view(img):
    """Detect apakah image adalah single-channel view (hanya R, G, atau B non-zero)."""
    if img is None or len(img.shape) != 3 or img.shape[2] != 3:
        return False
    b, g, r = cv2.split(img)
    b_sum = np.sum(b)
    g_sum = np.sum(g)
    r_sum = np.sum(r)
    channels_with_data = sum([b_sum > 0, g_sum > 0, r_sum > 0])
    return channels_with_data == 1

def reset_state_on_upload(img, filename):
    """Reset state saat upload/load gambar baru."""
    image_state['original'] = img.copy()
    image_state['current'] = img.copy()
    image_state['history'] = []
    image_state['adjustment_base'] = None
    image_state['original_dims'] = img.shape[:2] if img is not None else None
    image_state['filename'] = filename
    image_state['before_channel_view'] = None

# =============================================
# ROUTES
# =============================================

@app.route('/')
def index():
    original_b64 = numpy_to_base64(image_state['original'])
    current_b64 = numpy_to_base64(image_state['current'])
    hist_ori_b64 = generate_histogram_base64(image_state['original'])
    hist_proc_b64 = generate_histogram_base64(image_state['current'])
    can_undo = len(image_state['history']) > 0
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
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is not None:
        reset_state_on_upload(img, file.filename or 'image.png')
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
    reset_state_on_upload(img, f"sample_{color}.png")
    return redirect(url_for('index'))

@app.route('/reset')
def reset_image():
    image_state['original'] = None
    image_state['current'] = None
    image_state['history'] = []
    image_state['adjustment_base'] = None
    image_state['original_dims'] = None
    image_state['filename'] = 'image.png'
    image_state['before_channel_view'] = None
    return redirect(url_for('index'))

@app.route('/download')
def download_image():
    if image_state['current'] is None:
        return redirect(url_for('index'))
    fmt = request.args.get('format', 'png').lower()
    filename = request.args.get('filename', 'hasil-edit').strip()
    if fmt not in ['png', 'jpg', 'bmp']:
        fmt = 'png'
    filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_')).strip()
    if not filename:
        filename = 'hasil-edit'
    img = image_state['current']
    if not is_valid_image(img):
        return redirect(url_for('index'))
    img = ensure_bgr(img)
    ext = '.jpg' if fmt == 'jpg' else f'.{fmt}'
    mime = 'image/jpeg' if fmt == 'jpg' else f'image/{fmt}'
    params = [cv2.IMWRITE_JPEG_QUALITY, 95] if fmt == 'jpg' else []
    success, buffer = cv2.imencode(ext, img, params)
    if not success:
        return redirect(url_for('index'))
    return send_file(
        io.BytesIO(buffer.tobytes()),
        mimetype=mime,
        as_attachment=True,
        download_name=f"{filename}{ext}"
    )

# =============================================
# API — UNDO / RESET
# =============================================

@app.route('/api/undo', methods=['POST'])
def undo():
    if len(image_state['history']) == 0:
        return jsonify({'error': 'Tidak ada yang bisa di-undo'}), 400
    image_state['current'] = image_state['history'].pop()
    image_state['adjustment_base'] = None
    image_state['before_channel_view'] = None  # Clear channel view state saat undo
    current_b64 = numpy_to_base64(image_state['current'])
    hist_b64 = generate_histogram_base64(image_state['current'])
    can_undo = len(image_state['history']) > 0
    return jsonify({'processed_image': current_b64, 'hist_proc': hist_b64, 'can_undo': can_undo})

@app.route('/api/reset_to_original', methods=['POST'])
def reset_to_original():
    if image_state['original'] is None:
        return jsonify({'error': 'Belum ada gambar'}), 400
    push_history(image_state['current'])
    image_state['current'] = image_state['original'].copy()
    image_state['adjustment_base'] = None
    image_state['before_channel_view'] = None  # Clear channel view state
    current_b64 = numpy_to_base64(image_state['current'])
    hist_b64 = generate_histogram_base64(image_state['current'])
    return jsonify({'processed_image': current_b64, 'hist_proc': hist_b64, 'can_undo': True})

@app.route('/api/begin_adjust', methods=['POST'])
def begin_adjust():
    """Simpan snapshot saat user mulai menyentuh slider."""
    if image_state['current'] is not None:
        image_state['adjustment_base'] = image_state['current'].copy()
    return jsonify({'ok': True})

# =============================================
# API — PROCESS
# =============================================

@app.route('/api/process', methods=['POST'])
def process_image_api():
    if image_state['current'] is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.json
    action = data.get('action')
    params = data.get('params', {})

    if action not in VALID_ACTIONS:
        return jsonify({'error': f'Action tidak dikenal: {action}'}), 400

    try:
        is_preview = params.get('_preview', False)

        if is_preview:
            base = image_state['adjustment_base']
            img = base.copy() if base is not None else image_state['current'].copy()
        else:
            image_state['adjustment_base'] = None

            # State Management perbaikan Undo berurutan untuk fitur Color Channel Split
            if action == 'color_channel':
                if image_state['before_channel_view'] is None:
                    image_state['before_channel_view'] = image_state['current'].copy()

                push_history(image_state['current'])
                img = image_state['before_channel_view'].copy()

            elif action != 'color_channel' and image_state['before_channel_view'] is not None:
                if is_single_channel_view(image_state['current']):
                    img = image_state['before_channel_view'].copy()
                    push_history(img)
                    image_state['before_channel_view'] = None  # Clear channel view mode
                else:
                    push_history(image_state['current'])
                    img = image_state['current'].copy()
            else:
                push_history(image_state['current'])
                img = image_state['current'].copy()

        if not is_valid_image(img):
            return jsonify({'error': 'Gambar tidak valid'}), 400

        img = ensure_bgr(img)
        out_img = img.copy()

        # ══════════════════════════════════════════════════════════════
        # PROSES UTAMA
        # ══════════════════════════════════════════════════════════════

        if action == 'grayscale':
            out_img = apply_grayscale(img)

        elif action == 'histogram_equalization':
            out_img = apply_histogram_equalization(img)

        elif action == 'brightness_contrast':
            out_img = apply_brightness_contrast(img, params)

        elif action == 'saturation':
            out_img = apply_saturation(img, params)

        elif action == 'hue_rotate':
            out_img = apply_hue_rotate(img, params)

        elif action == 'color_channel':
            if image_state['before_channel_view'] is None:
                image_state['before_channel_view'] = image_state['current'].copy()

            out_img = apply_color_channel(img, params)

            # Selaraskan out_img ke state global agar konsisten dicatat history di pipeline utama
            if not is_preview:
                image_state['current'] = out_img.copy()

        elif action == 'sharpening':
            out_img = apply_sharpening(img)

        elif action == 'blur_filter':
            out_img = apply_blur(img, params)

        elif action == 'rotate':
            out_img = apply_rotate(img, params)

        elif action == 'flip':
            out_img = apply_flip(img, params)

        elif action == 'resize':
            out_img = apply_resize(img, params)

        elif action == 'crop_center':
            out_img = apply_crop_center(img)

        elif action == 'crop_manual':
            out_img = apply_crop_manual(img, params)

        elif action == 'add_text':
            text = params.get('text', 'Teks')
            if not text.strip():
                text = 'Teks'
            size = float(params.get('size', 32))
            x = int(params.get('x', 20))
            y = int(params.get('y', 50))
            color_hex = params.get('color', '#ffffff').lstrip('#')
            try:
                r2 = int(color_hex[0:2], 16)
                g2 = int(color_hex[2:4], 16)
                b2 = int(color_hex[4:6], 16)
            except Exception:
                r2, g2, b2 = 255, 255, 255
            font_scale = size / 20.0
            thickness = max(1, int(font_scale * 2))
            out_img = img.copy()
            cv2.putText(out_img, text, (x + 2, y + 2), cv2.FONT_HERSHEY_DUPLEX,
                        font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
            cv2.putText(out_img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX,
                        font_scale, (b2, g2, r2), thickness, cv2.LINE_AA)

        elif action == 'edge_detection':
            out_img = apply_edge_detection(img, params)

        elif action == 'edge_robert':
            out_img = apply_edge_robert(img)

        elif action == 'edge_log':
            out_img = apply_edge_log(img)

        elif action == 'morphology':
            out_img = apply_morphology(img, params)

        elif action == 'compress':
            out_img = apply_compress_jpeg(img, params)

        elif action == 'compress_rle':
            out_img = apply_compress_rle(img)

        elif action == 'translation':
            out_img = apply_translation(img, params)

        elif action == 'noise_saltpepper':
            out_img = apply_noise_saltpepper(img, params)

        elif action == 'noise_removal_sp':
            out_img = apply_noise_removal(img, params)

        elif action == 'threshold':
            out_img = apply_threshold(img, params)

        elif action == 'segmentation_threshold':
            out_img = apply_segmentation_threshold(img, params)

        elif action == 'segmentation_edge':
            out_img = apply_segmentation_edge(img)

        elif action == 'segmentation_region':
            out_img = apply_segmentation_region(img)

        elif action == 'interpolation':
            out_img = apply_interpolation(img, params)

        # ══════════════════════════════════════════════════════════════
        # UPDATE STATE
        # ══════════════════════════════════════════════════════════════
        if not is_preview:
            if not is_valid_image(out_img):
                return jsonify({'error': 'Operasi menghasilkan gambar tidak valid'}), 400
            image_state['current'] = out_img.copy()

        current_b64 = numpy_to_base64(out_img)
        hist_b64 = generate_histogram_base64(out_img)
        can_undo = len(image_state['history']) > 0

        return jsonify({
            'processed_image': current_b64,
            'hist_proc': hist_b64,
            'can_undo': can_undo
        })

    except Exception as e:
        import traceback
        error_msg = f"Error di action '{action}': {str(e)}"
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500


if __name__ == '__main__':
    app.run(debug=True)

# =========================================================================
# 2. TAMBAHAN: BLOK EKSEKUSI SERVER DI BAGIAN PALING BAWAH FILE
# =========================================================================
# Blok ini wajib berada di baris paling terakhir dari file app.py Anda.
# Berfungsi untuk menangkap Port dinamis dari server Render secara otomatis.
if __name__ == '__main__':
    # Mengambil port environment dari Render, default ke 5000 jika dijalankan lokal
    port = int(os.environ.get("PORT", 5000))
    # Jalankan menggunakan host biner universal (0.0.0.0) agar bisa diakses publik
    app.run(host='0.0.0.0', port=port, debug=False)
# =========================================================================