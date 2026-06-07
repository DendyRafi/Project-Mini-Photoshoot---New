import cv2

def apply_brightness_contrast(img, params):
    b_val = int(params.get('brightness', 0))
    c_val = float(params.get('contrast', 1.0))
    return cv2.convertScaleAbs(img, alpha=c_val, beta=b_val)

def apply_histogram_equalization(img):
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)