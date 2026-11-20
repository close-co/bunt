import logging
import os

import click
import extcolors
import pandas as pd
from PIL import Image
from tqdm import tqdm

from bunt.colors.utils import get_images, rgb_to_hex

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
@click.option('--dataset-input-path', default='Dataset', help='File path where the dataset that is gonna be tagged is located')
def tag(dataset_input_path):
    df_products = pd.read_parquet(os.path.join(dataset_input_path, 'products.parquet'))
    
    # Backup dataset
    df_products.to_parquet(os.path.join(dataset_input_path, 'products_backup.parquet'))
    
    images_folder = os.path.join(dataset_input_path, 'images-segmented')

    logger.info(f"Segmenting images in dataset: {dataset_input_path}")
    # N products found
    logger.info(f"Found {len(df_products)} products in products.parquet")

    # List all the folder in folder images
    # tqdm for progress bar
    for folder_product in tqdm(os.listdir(images_folder), desc="Processing folders"):
        folder_path = os.path.join(images_folder, folder_product)
        if os.path.isdir(folder_path):
            for image_name in os.listdir(folder_path):
                image_path = os.path.join(folder_path, image_name)
                image = Image.open(image_path).convert("RGB")

                extracted_colors = extcolors.extract_from_image(image, tolerance=TOLERANCE, limit=LIMIT)
                df_product_colors = colors_to_df(extracted_colors)
                df_product_colors = df_product_colors[df_product_colors['occurence'] == df_product_colors['occurence'].max()]
                product_id = folder_product
                df_products.loc[df_products['product_id'] == product_id, df_product_colors.columns] = df_product_colors.iloc[0].values

    tagged_products_percentage = (~df_products['primary_color'].isna()).sum() / len(df_products)
    logger.info(f"{tagged_products_percentage*100}% of products were tagged")

    df_products.to_parquet(os.path.join(dataset_input_path, "products.parquet"))

if __name__ == '__main__':
    cli()
