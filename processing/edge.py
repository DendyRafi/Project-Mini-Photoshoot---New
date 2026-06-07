import cv2
import numpy as np

def ensure_bgr(img):
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img

def apply_edge_detection(img, params):
    method = params.get('method', 'canny')
    gray   = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if method == 'canny':
        out = cv2.Canny(gray, 50, 150)
    elif method == 'sobel':
        sx  = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sy  = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        out = cv2.convertScaleAbs(np.sqrt(sx**2 + sy**2))
    elif method == 'laplacian':
        out = cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_64F))
    elif method == 'prewitt':
        kx  = np.array([[1,0,-1],[1,0,-1],[1,0,-1]], dtype=np.float32)
        ky  = np.array([[1,1,1],[0,0,0],[-1,-1,-1]], dtype=np.float32)
        px  = cv2.filter2D(gray, -1, kx)
        py  = cv2.filter2D(gray, -1, ky)
        out = cv2.convertScaleAbs(np.sqrt(px.astype(np.float32)**2 + py.astype(np.float32)**2))
    else:
        out = cv2.Canny(gray, 50, 150)
    return ensure_bgr(out)

def apply_edge_robert(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    kx   = np.array([[1,0],[0,-1]], dtype=np.float32)
    ky   = np.array([[0,1],[-1,0]], dtype=np.float32)
    px   = cv2.filter2D(gray, -1, kx)
    py   = cv2.filter2D(gray, -1, ky)
    out  = cv2.convertScaleAbs(np.sqrt(px**2 + py**2))
    return ensure_bgr(out)

def apply_edge_log(img):
    gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    out     = cv2.convertScaleAbs(cv2.Laplacian(blurred, cv2.CV_64F))
    return ensure_bgr(out)