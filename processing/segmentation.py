import cv2
import numpy as np

def apply_segmentation_threshold(img, params):
    thresh_val = int(params.get('value', 127))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
    return cv2.bitwise_and(img, img, mask=mask)

def apply_segmentation_edge(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = img.copy()
    cv2.drawContours(out, contours, -1, (87, 255, 168), 2)
    return out

def apply_segmentation_region(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    dist = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist, 0.5 * dist.max(), 255, 0)
    sure_fg  = sure_fg.astype(np.uint8)
    unknown  = cv2.subtract(thresh, sure_fg)
    _, markers = cv2.connectedComponents(sure_fg)
    markers  = markers + 1
    markers[unknown == 255] = 0
    markers  = cv2.watershed(img, markers)
    out      = img.copy()
    out[markers == -1] = [87, 255, 168]
    return out