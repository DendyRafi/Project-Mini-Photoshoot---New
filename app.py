from flask import Flask, render_template, request
import os

from processing.grayscale import grayscale_image
from processing.blur import blur_image
from processing.sharpen import sharpen_image
from processing.threshold import threshold_image
from processing.edge import edge_image
from processing.transform import resize_image, rotate_image, flip_image

app = Flask(__name__)

# Folder upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Halaman utama
@app.route('/')
def index():
    return render_template('index.html')


# Upload gambar
@app.route('/upload', methods=['POST'])
def upload():

    # cek file
    if 'image' not in request.files:
        return "Tidak ada file"

    file = request.files['image']

    # cek nama kosong
    if file.filename == '':
        return "Belum pilih file"

    # simpan gambar
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # kirim nama file ke HTML
    return render_template(
        'index.html',
        filename=file.filename
    )

@app.route('/grayscale/<filename>')
def grayscale(filename):

    # lokasi gambar asli
    input_path = os.path.join('static/uploads', filename)

    # nama output
    output_filename = 'gray_' + filename

    # lokasi hasil
    output_path = os.path.join('static/outputs', output_filename)

    # proses grayscale
    grayscale_image(input_path, output_path)

    # tampilkan hasil
    return render_template(
        'index.html',
        filename=filename,
        output_image=output_filename
    )

@app.route('/blur/<filename>')
def blur(filename):

    input_path = os.path.join('static/uploads', filename)

    output_filename = 'blur_' + filename

    output_path = os.path.join('static/outputs', output_filename)

    blur_image(input_path, output_path)

    return render_template(
        'index.html',
        filename=filename,
        output_image=output_filename
    )

@app.route('/sharpen/<filename>')
def sharpen(filename):

    input_path = os.path.join('static/uploads', filename)

    output_filename = 'sharpen_' + filename

    output_path = os.path.join('static/outputs', output_filename)

    sharpen_image(input_path, output_path)

    return render_template(
        'index.html',
        filename=filename,
        output_image=output_filename
    )

@app.route('/threshold/<filename>')
def threshold(filename):

    input_path = os.path.join('static/uploads', filename)

    output_filename = 'threshold_' + filename

    output_path = os.path.join('static/outputs', output_filename)

    threshold_image(input_path, output_path)

    return render_template(
        'index.html',
        filename=filename,
        output_image=output_filename
    )

@app.route('/edge/<filename>')
def edge(filename):

    input_path = os.path.join('static/uploads', filename)

    output_filename = 'edge_' + filename

    output_path = os.path.join('static/outputs', output_filename)

    edge_image(input_path, output_path)

    return render_template(
        'index.html',
        filename=filename,
        output_image=output_filename
    )


# Jalankan Flask
if __name__ == '__main__':
    app.run(debug=True)