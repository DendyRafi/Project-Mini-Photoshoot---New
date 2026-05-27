import os
import time
import cv2
from flask import Flask, render_template, request, redirect, url_for, send_file

app = Flask(__name__)

# Konfigurasi folder menggunakan path relatif yang bersih tanpa slash di awal
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_OUTPUT'] = OUTPUT_FOLDER

# Pastikan direktori folder aman & tersedia
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Menyimpan riwayat path berkas gambar aktif
current_image = {
    'original': None,
    'processed': None
}

@app.route('/')
def index():
    return render_template('index.html', 
                           original_image=current_image['original'], 
                           processed_image=current_image['processed'])

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(request.url)
    
    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        # Menambahkan format timestamp agar nama berkas selalu unik & menghindari cache browser
        timestamp = int(time.time())
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Simpan path dengan standarisasi garis miring (replace backslash jika di Windows)
        clean_path = filepath.replace('\\', '/')
        current_image['original'] = clean_path
        current_image['processed'] = clean_path
        
        return redirect(url_for('index'))

# --- ROUTE FITUR EKSPERIMEN CITRA ---

@app.route('/process/grayscale')
def process_grayscale():
    if not current_image['original']:
        return redirect(url_for('index'))
    
    # Baca gambar asli
    img = cv2.imread(current_image['original'])
    
    # Eksekusi konversi ruang warna
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Buat nama file keluaran baru
    out_filename = "gray_" + os.path.basename(current_image['original'])
    out_filepath = os.path.join(app.config['UPLOAD_OUTPUT'], out_filename).replace('\\', '/')
    
    # Simpan hasil olahan
    cv2.imwrite(out_filepath, gray_img)
    
    # Update status preview kanan
    current_image['processed'] = out_filepath
    return redirect(url_for('index'))


@app.route('/process/blur')
def process_blur():
    if not current_image['original']:
        return redirect(url_for('index'))
        
    img = cv2.imread(current_image['original'])
    
    # Menggunakan metode Gaussian Blur dengan kernel matriks berukuran (15, 15)
    blur_img = cv2.GaussianBlur(img, (15, 15), 0)
    
    out_filename = "blur_" + os.path.basename(current_image['original'])
    out_filepath = os.path.join(app.config['UPLOAD_OUTPUT'], out_filename).replace('\\', '/')
    
    cv2.imwrite(out_filepath, blur_img)
    
    current_image['processed'] = out_filepath
    return redirect(url_for('index'))


@app.route('/download')
def download_image():
    if current_image['processed'] and os.path.exists(current_image['processed']):
        return send_file(current_image['processed'], as_attachment=True)
    return redirect(url_for('index'))


# TAMBAHAN: Rute untuk mengosongkan gambar (Tombol Reset di kiri bawah HTML)
@app.route('/reset')
def reset_image():
    current_image['original'] = None
    current_image['processed'] = None
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Menggunakan debug=True sangat baik saat masa pengembangan/development
    app.run(debug=True)