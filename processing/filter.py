import cv2
import numpy as np

def apply_blur(img, params):
    filter_type = params.get('type', 'gaussian')
    k_size = int(params.get('kernel', 5))
    if k_size % 2 == 0: k_size += 1
    if filter_type == 'gaussian':
        return cv2.GaussianBlur(img, (k_size, k_size), 0)
    elif filter_type == 'median':
        return cv2.medianBlur(img, k_size)
    return img.copy()

def apply_sharpening(img):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)

def apply_noise_saltpepper(img, params):
    amount  = float(params.get('amount', 0.02))
    out     = img.copy()
    total   = int(amount * out.size)
    coords  = [np.random.randint(0, i, total // 2) for i in out.shape[:2]]
    out[coords[0], coords[1]] = 255
    coords  = [np.random.randint(0, i, total // 2) for i in out.shape[:2]]
    out[coords[0], coords[1]] = 0
    return out

def apply_noise_removal(img, params):
    k_size = int(params.get('kernel', 3))
    if k_size % 2 == 0: k_size += 1
    return cv2.medianBlur(img, k_size)