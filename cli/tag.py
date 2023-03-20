import logging
import os

import click
import extcolors
import pandas as pd
from PIL import Image

from colors.utils import get_images

logger = logging.getLogger("close")
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

PERCENTAGE_THRESHOLD = 0.4
TOLERANCE = 10


def resize(img):
    output_width = 300
    wpercent = (output_width / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((output_width, hsize), resample=Image.ANTIALIAS)
    return img


def colors_to_df(extracted_colors):
    df_colors = pd.DataFrame(columns=['red', 'green', 'blue', 'occurence'])
    total_occurence = extracted_colors[1]
    for color in extracted_colors[0]:
        rgb_color = color[0]
        occurence = color[1]
        df_color = pd.DataFrame({
            "red": [rgb_color[0]],
            "green": [rgb_color[1]],
            "blue": [rgb_color[2]],
            "occurence": [occurence]
        })
        df_colors = pd.concat([df_colors, df_color])
    df_colors['occurence'] = df_colors['occurence'] / total_occurence
    return df_colors


@click.command()
@click.option('--dataset-path', default='.', help='File path where the dataset that is gonna be tagged is located')
def tag(dataset_path):
    df_products = pd.DataFrame()
    for image, filename, root in get_images(os.path.join(dataset_path, 'images')):
        width, height = image.size
        crop_size = (int(width * 0.05), int(height * 0.05), int(width * 0.95), int(height * 0.95))
        image = image.crop(crop_size)

        path_as_array = root.split(os.sep)
        product_id = path_as_array[-1]

        logger.info(f"Generating color palette for product {product_id}")
        image = resize(image)
        extracted_colors = extcolors.extract_from_image(image, tolerance=TOLERANCE, limit=6)
        df_product_colors = colors_to_df(extracted_colors)
        df_product_colors = df_product_colors[df_product_colors['occurence'] > PERCENTAGE_THRESHOLD]
        df_product_colors['product_id'] = product_id

        df_products = pd.concat([df_products, df_product_colors])
    df_products.reset_index(drop=True).to_parquet("product_colors.parquet")


if __name__ == '__main__':
    tag()
