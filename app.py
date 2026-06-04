import os
import time
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_OUTPUT'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

current_image = {
    'original': None,
    'processed': None
}

def generate_histogram(img_path, output_name):
    img = cv2.imread(img_path)
    if img is None:
        return None
    plt.figure(figsize=(4, 2.5), facecolor='#17171a')
    ax = plt.axes()
    ax.set_facecolor('#1e1e22')
    ax.tick_params(colors='#9494a0', labelsize=8)
    if len(img.shape) == 2 or (len(img.shape) == 3 and np.all(img[:,:,0] == img[:,:,1]) and np.all(img[:,:,0] == img[:,:,2])):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        plt.plot(hist, color='#a8ff57', linewidth=1.5)
    else:
        colors = ('b', 'g', 'r')
        hex_colors = ('#38bdf8', '#4ade80', '#ff5252')
        for i, col in enumerate(colors):
            hist = cv2.calcHist([img], [i], None, [256], [0, 256])
            plt.plot(hist, color=hex_colors[i], linewidth=1.5, label=col.upper())
    plt.xlim([0, 256])
    plt.tight_layout()
    hist_path = os.path.join(app.config['UPLOAD_OUTPUT'], output_name)
    plt.savefig(hist_path, bbox_inches='tight', dpi=100)
    plt.close()
    return hist_path.replace('\\', '/')

@app.route('/')
def index():
    hist_ori = None
    hist_proc = None
    if current_image['original']:
        hist_ori = generate_histogram(current_image['original'], "hist_ori.png")
    if current_image['processed']:
        hist_proc = generate_histogram(current_image['processed'], "hist_proc.png")
    return render_template('index.html',
                           original_image=current_image['original'],
                           processed_image=current_image['processed'],
                           hist_original=hist_ori,
                           hist_processed=hist_proc)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(request.url)
    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)
    if file:
        timestamp = int(time.time())
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
        file.save(filepath)
        current_image['original'] = filepath
        current_image['processed'] = filepath
        return redirect(url_for('index'))

@app.route('/reset')
def reset_image():
    current_image['original'] = None
    current_image['processed'] = None
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
    filename = f"sample_{color}.png"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
    cv2.imwrite(filepath, img)
    current_image['original'] = filepath
    current_image['processed'] = filepath
    return redirect(url_for('index'))

@app.route('/download')
def download_image():
    if current_image['processed'] and os.path.exists(current_image['processed']):
        return send_file(current_image['processed'], as_attachment=True)
    return redirect(url_for('index'))

@app.route('/api/process', methods=['POST'])
def process_image_api():
    if not current_image['original']:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.json
    action = data.get('action')
    params = data.get('params', {})

    img = cv2.imread(current_image['original'])
    if img is None:
        return jsonify({'error': 'Gambar tidak bisa dibaca'}), 400
    out_img = img.copy()

    if action == 'grayscale':
        out_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    elif action == 'histogram_equalization':
        if len(img.shape) == 3:
            ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
            out_img = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        else:
            out_img = cv2.equalizeHist(img)

    elif action == 'brightness_contrast':
        b_val = int(params.get('brightness', 0))
        c_val = float(params.get('contrast', 1.0))
        out_img = cv2.convertScaleAbs(img, alpha=c_val, beta=b_val)

    elif action == 'saturation':
        value = float(params.get('value', 1.0))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] = np.clip(hsv[:,:,1] * value, 0, 255)
        out_img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    elif action == 'hue_rotate':
        angle = int(params.get('angle', 0))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.int32)
        hsv[:,:,0] = (hsv[:,:,0] + angle) % 180
        out_img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    elif action == 'color_channel':
        channel = params.get('channel', 'R')
        b, g, r = cv2.split(img)
        blank = np.zeros_like(b)
        if channel == 'R':
            out_img = cv2.merge([blank, blank, r])
        elif channel == 'G':
            out_img = cv2.merge([blank, g, blank])
        elif channel == 'B':
            out_img = cv2.merge([b, blank, blank])

    elif action == 'sharpening':
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        out_img = cv2.filter2D(img, -1, kernel)

    elif action == 'blur_filter':
        filter_type = params.get('type', 'gaussian')
        k_size = int(params.get('kernel', 5))
        if k_size % 2 == 0:
            k_size += 1
        if filter_type == 'gaussian':
            out_img = cv2.GaussianBlur(img, (k_size, k_size), 0)
        elif filter_type == 'median':
            out_img = cv2.medianBlur(img, k_size)
        elif filter_type == 'sharpening':
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            out_img = cv2.filter2D(img, -1, kernel)

    elif action == 'rotate':
        angle = int(params.get('angle', 0))
        h, w = img.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        out_img = cv2.warpAffine(img, M, (w, h))

    elif action == 'flip':
        direction = params.get('direction', 'horizontal')
        flip_code = 1 if direction == 'horizontal' else 0
        out_img = cv2.flip(img, flip_code)

    elif action == 'resize':
        scale = float(params.get('scale', 100)) / 100.0
        out_img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

    elif action == 'crop_center':
        h, w = img.shape[:2]
        cy, cx = h // 2, w // 2
        half = min(cy, cx)
        out_img = img[cy - half:cy + half, cx - half:cx + half]

    elif action == 'crop_manual':
        x = int(params.get('x', 0))
        y = int(params.get('y', 0))
        w = int(params.get('w', img.shape[1]))
        h = int(params.get('h', img.shape[0]))
        x = max(0, x)
        y = max(0, y)
        w = min(w, img.shape[1] - x)
        h = min(h, img.shape[0] - y)
        if w > 0 and h > 0:
            out_img = img[y:y + h, x:x + w]
        else:
            out_img = img.copy()

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
        bgr_color = (b2, g2, r2)
        font_scale = size / 20.0
        thickness = max(1, int(font_scale * 2))
        out_img = img.copy()
        # Bayangan hitam agar teks terbaca di semua background
        cv2.putText(out_img, text, (x + 2, y + 2),
                    cv2.FONT_HERSHEY_DUPLEX, font_scale,
                    (0, 0, 0), thickness + 2, cv2.LINE_AA)
        # Teks utama
        cv2.putText(out_img, text, (x, y),
                    cv2.FONT_HERSHEY_DUPLEX, font_scale,
                    bgr_color, thickness, cv2.LINE_AA)

    elif action == 'edge_detection':
        method = params.get('method', 'canny')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if method == 'canny':
            out_img = cv2.Canny(gray, 50, 150)
        elif method == 'sobel':
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            out_img = cv2.convertScaleAbs(np.sqrt(sobelx ** 2 + sobely ** 2))
        elif method == 'laplacian':
            out_img = cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_64F))

    elif action == 'morphology':
        m_type = params.get('type', 'erosion')
        k_size = int(params.get('kernel', 3))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        kernel = np.ones((k_size, k_size), np.uint8)
        if m_type == 'erosion':
            out_img = cv2.erode(thresh, kernel, iterations=1)
        elif m_type == 'dilation':
            out_img = cv2.dilate(thresh, kernel, iterations=1)

    elif action == 'compress':
        quality = int(params.get('quality', 90))
        out_filename = f"compress_{quality}_" + os.path.basename(current_image['original'])
        out_filepath = os.path.join(app.config['UPLOAD_OUTPUT'], out_filename).replace('\\', '/')
        cv2.imwrite(out_filepath, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        current_image['processed'] = out_filepath
        return jsonify({'processed_image': out_filepath, 'reload_hist': True})

    elif action == 'cnn_detect':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            if cv2.contourArea(c) > 500:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(out_img, (x, y), (x + w, y + h), (87, 255, 168), 2)
                cv2.putText(out_img, "Objek Terdeteksi", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (87, 255, 168), 1)

    out_filename = f"proc_{action}_" + os.path.basename(current_image['original'])
    out_filepath = os.path.join(app.config['UPLOAD_OUTPUT'], out_filename).replace('\\', '/')
    cv2.imwrite(out_filepath, out_img)
    current_image['processed'] = out_filepath
    return jsonify({'processed_image': out_filepath, 'reload_hist': True})

if __name__ == '__main__':
    app.run(debug=True)