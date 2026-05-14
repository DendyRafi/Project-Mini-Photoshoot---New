import cv2

def resize_image(input_path, output_path):

    image = cv2.imread(input_path)

    resize = cv2.resize(image, (300, 300))

    cv2.imwrite(output_path, resize)

def rotate_image(input_path, output_path):

    image = cv2.imread(input_path)

    rotate = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    cv2.imwrite(output_path, rotate)

def flip_image(input_path, output_path):

    image = cv2.imread(input_path)

    flip = cv2.flip(image, 1)

    cv2.imwrite(output_path, flip)