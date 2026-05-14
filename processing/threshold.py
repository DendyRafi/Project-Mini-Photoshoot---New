import cv2

def threshold_image(input_path, output_path):

    image = cv2.imread(input_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    cv2.imwrite(output_path, thresh)