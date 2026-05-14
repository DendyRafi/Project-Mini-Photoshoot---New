import cv2
import numpy as np

def sharpen_image(input_path, output_path):

    image = cv2.imread(input_path)

    kernel = np.array([
        [0, -1, 0],
        [-1, 5,-1],
        [0, -1, 0]
    ])

    sharpen = cv2.filter2D(image, -1, kernel)

    cv2.imwrite(output_path, sharpen)