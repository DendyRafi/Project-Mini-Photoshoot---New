import cv2
import numpy as np

def apply_grayscale(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def apply_color_channel(img, params):
    channel = params.get('channel', 'R')
    b, g, r = cv2.split(img)
    blank   = np.zeros_like(b)
    if channel == 'R':   return cv2.merge([blank, blank, r])
    elif channel == 'G': return cv2.merge([blank, g, blank])
    elif channel == 'B': return cv2.merge([b, blank, blank])
    return img.copy()

def apply_saturation(img, params):
    value = float(params.get('value', 1.0))
    hsv   = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * value, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def apply_hue_rotate(img, params):
    angle = int(params.get('angle', 0))
    hsv   = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.int32)
    hsv[:, :, 0] = (hsv[:, :, 0] + angle) % 180
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)