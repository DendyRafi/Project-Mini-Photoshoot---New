import cv2

def red_channel(input_path, output_path):

    image = cv2.imread(input_path)

    b, g, r = cv2.split(image)

    zeros = b * 0

    red = cv2.merge([zeros, zeros, r])

    cv2.imwrite(output_path, red)