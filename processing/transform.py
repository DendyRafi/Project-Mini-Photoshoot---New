import cv2
import numpy as np

def apply_rotate(img, params):
    angle = int(params.get('angle', 0))
    h, w  = img.shape[:2]
    M     = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h))

def apply_flip(img, params):
    direction = params.get('direction', 'horizontal')
    return cv2.flip(img, 1 if direction == 'horizontal' else 0)

def apply_resize(img, params):
    scale = float(params.get('scale', 100)) / 100.0
    return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

def apply_crop_center(img):
    h, w   = img.shape[:2]
    cy, cx = h//2, w//2
    half   = min(cy, cx)
    return img[cy-half:cy+half, cx-half:cx+half].copy()

def apply_crop_manual(img, params):
    x = max(0, int(params.get('x', 0)))
    y = max(0, int(params.get('y', 0)))
    w = int(params.get('w', img.shape[1]))
    h = int(params.get('h', img.shape[0]))
    w = min(w, img.shape[1] - x)
    h = min(h, img.shape[0] - y)
    if w > 0 and h > 0:
        return img[y:y+h, x:x+w].copy()
    return img.copy()

def apply_translation(img, params):
    tx = int(params.get('tx', 0))
    ty = int(params.get('ty', 0))
    h, w = img.shape[:2]
    M    = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(img, M, (w, h))

def apply_interpolation(img, params):
    scale  = float(params.get('scale', 1.5))
    method = params.get('method', 'bilinear')
    interp = cv2.INTER_LINEAR if method == 'bilinear' else cv2.INTER_NEAREST
    return cv2.resize(img, None, fx=scale, fy=scale, interpolation=interp)