import cv2
import numpy as np

def apply_compress_jpeg(img, params):
    quality = max(5, min(100, int(params.get('quality', 80))))
    success, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if success:
        file_bytes = np.frombuffer(buffer, np.uint8)
        return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return img.copy()

def apply_compress_rle(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    flat = gray.flatten()
    runs, count = [], 1
    for i in range(1, len(flat)):
        if flat[i] == flat[i-1]:
            count += 1
        else:
            runs.append((flat[i-1], count))
            count = 1
    runs.append((flat[-1], count))
    decoded = np.array([v for val, cnt in runs for v in [val]*cnt],
                       dtype=np.uint8).reshape(gray.shape)
    out   = cv2.cvtColor(decoded, cv2.COLOR_GRAY2BGR)
    ratio = len(flat) / (len(runs) * 2) if runs else 1
    cv2.putText(out, f"RLE Ratio: {ratio:.2f}x",
                (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (87, 255, 168), 2)
    return out