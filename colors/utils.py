import os
from PIL import Image


def get_images(dataset_path):
    for root, dirnames, filenames in os.walk(dataset_path):
        filenames = [filename for filename in filenames if filename != '.DS_Store']
        for filename in filenames:
            image_path = os.path.join(root, filename)
            image = Image.open(image_path)
            yield image, filename, root
            image.close()
