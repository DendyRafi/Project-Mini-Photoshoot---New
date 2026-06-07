import cv2
import numpy as np

def ensure_bgr(img):
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img

def apply_morphology(img, params):
    m_type = params.get('type', 'erosion')
    k_size = int(params.get('kernel', 3))
    gray   = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    unique_vals = np.unique(gray)
    if len(unique_vals) <= 2 and 255 in unique_vals:
        thresh = gray
    else:
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    kernel = np.ones((k_size, k_size), np.uint8)
    if m_type == 'erosion':
        out = cv2.erode(thresh, kernel, iterations=1)
    elif m_type == 'dilation':
        out = cv2.dilate(thresh, kernel, iterations=1)
    else:
        out = thresh
    return ensure_bgr(out)

def apply_threshold(img, params):
    thresh_val = int(params.get('value', 127))
    method     = params.get('method', 'binary')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if method == 'binary':
        _, t = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
    elif method == 'binary_inv':
        _, t = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
    elif method == 'otsu':
        _, t = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method == 'adaptive':
        t = cv2.adaptiveThreshold(gray, 255,
              cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    else:
        _, t = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
    return ensure_bgr(t)