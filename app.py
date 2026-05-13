from flask import Flask, render_template, request
import os

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

# Jalankan Flask
if __name__ == '__main__':
    app.run(debug=True)