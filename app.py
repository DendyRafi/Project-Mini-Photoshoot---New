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

    # cek apakah ada file
    if 'image' not in request.files:
        return "Tidak ada file"

    file = request.files['image']

    # cek nama file kosong
    if file.filename == '':
        return "File belum dipilih"

    # simpan file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    return f"Gambar berhasil diupload: {file.filename}"


# Jalankan Flask
if __name__ == '__main__':
    app.run(debug=True)