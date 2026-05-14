import cv2

def blur_image(input_path, output_path):

    image = cv2.imread(input_path)

    blur = cv2.GaussianBlur(image, (15, 15), 0)

    cv2.imwrite(output_path, blur)