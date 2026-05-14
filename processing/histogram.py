import cv2
import matplotlib.pyplot as plt

def histogram_image(input_path, output_path):

    image = cv2.imread(input_path, 0)

    plt.hist(image.ravel(), 256, [0,256])

    plt.savefig(output_path)

    plt.close()