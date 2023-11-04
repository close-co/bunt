import os
from PIL import Image
from typing import Tuple


def get_images(dataset_path):
    for root, dirnames, filenames in os.walk(dataset_path):
        filenames = [filename for filename in filenames if filename != '.DS_Store']
        for filename in filenames:
            image_path = os.path.join(root, filename)
            image = Image.open(image_path)
            yield image, filename, root
            image.close()

def rgb_to_hex(rgb_color: Tuple) -> str:
    return '#%02x%02x%02x' % rgb_color
