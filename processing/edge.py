import cv2

def edge_image(input_path, output_path):

    image = cv2.imread(input_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edge = cv2.Canny(gray, 100, 200)

    cv2.imwrite(output_path, edge)