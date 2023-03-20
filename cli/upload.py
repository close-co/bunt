import logging

import boto3
import click
import pandas as pd
from mercury.product import Product
from tqdm import tqdm


@click.command()
@click.option('--products-path', default='.', help='File path where the serialized object with products can be found')
def upload(products_path):
    dataset = pd.read_parquet(products_path)
    for product_id, color_feature in tqdm(dataset.groupby('product_id')):
        product = Product(product_id=product_id, stage='prod')
        main_color = color_feature.iloc[0]
        product.set_primary_color(main_color['red'], main_color['green'], main_color['blue'])
        if len(color_feature) == 2:
            secondary_color = color_feature.iloc[1]
            product.set_secondary_color(secondary_color['red'], secondary_color['green'], secondary_color['blue'])

        if len(color_feature) == 3:
            extra_color = color_feature.iloc[3]
            product.set_extra_color(extra_color['red'], extra_color['green'], extra_color['blue'])
        product.save()


if __name__ == '__main__':
    upload()
