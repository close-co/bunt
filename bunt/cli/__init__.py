import logging
import os

import click
import extcolors
import pandas as pd
from PIL import Image
from tqdm import tqdm
from colors.utils import get_images, rgb_to_hex

logger = logging.getLogger("close")
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

PERCENTAGE_THRESHOLD = 0.4
TOLERANCE = 10
LIMIT = 6
CROP_BORDER_SIZE = 0.09

def colors_to_df(extracted_colors):
    df_colors = pd.DataFrame(columns=['primary_color', 'secondary_color', 'tertiary_color', 'occurence'])
    total_occurence = extracted_colors[1]
    counter = 0
    for color in extracted_colors[0]:
        rgb_color = color[0]
        hex_color = rgb_to_hex(rgb_color)
        occurence = color[1]
        color_key = ''
        if counter == 0:
            color_key = 'primary_color'
        if counter == 1:
            color_key = 'secondary_color'
        if counter == 2:
            color_key = 'tertiary_color'
        if counter > 2:
            break
        counter += 1
        df_color = pd.DataFrame({
            color_key: [hex_color],
            "occurence": [occurence]
        })
        df_colors = pd.concat([df_colors, df_color])
    df_colors['occurence'] = df_colors['occurence'] / total_occurence
    return df_colors


def resize(img):
    output_width = 300
    wpercent = (output_width / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((output_width, hsize))
    return img


@click.group()
def cli():
    pass


@cli.command()
@click.option('--dataset-path', default='Dataset', help='File path where the dataset that is gonna be tagged is located')
def tag(dataset_path):
    df = pd.read_parquet(dataset_path+"/products.parquet").drop_duplicates(subset=['product_id']).set_index('product_id')
    df = df.drop(['primary_color'], axis=1, errors='ignore')
    df = df.drop(['occurence'], axis=1, errors='ignore')
    df_products = pd.DataFrame()
    for image, filename, root in tqdm(get_images(os.path.join(dataset_path, 'images'))):
        width, height = image.size
        crop_size = (int(width * CROP_BORDER_SIZE), int(height * CROP_BORDER_SIZE), int(width * 1-CROP_BORDER_SIZE), int(height * 1-CROP_BORDER_SIZE))
        image = image.crop(crop_size)

        path_as_array = root.split(os.sep)
        product_id = path_as_array[-1]

        image = resize(image)
        extracted_colors = extcolors.extract_from_image(image, tolerance=TOLERANCE, limit=LIMIT)
        df_product_colors = colors_to_df(extracted_colors)
        df_product_colors = df_product_colors[df_product_colors['occurence'] == df_product_colors['occurence'].max()]
        df_product_colors['product_id'] = product_id

        df_products = pd.concat([df_products, df_product_colors])

    df_products = df_products.set_index('product_id')
    df = df.join(df_products, on='product_id').reset_index()
    tagged_products_percentage = (~df['primary_color'].isna()).sum() / len(df)
    logger.info(f"{tagged_products_percentage*100}% of products were tagged")
    df = df.where(pd.notnull(df), None)
    df.to_parquet(dataset_path+"/products.parquet")


if __name__ == '__main__':
    cli()
