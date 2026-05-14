import cv2

def grayscale_image(input_path, output_path):

    # membaca gambar
    image = cv2.imread(input_path)

    # ubah ke grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # simpan hasil
    cv2.imwrite(output_path, gray)