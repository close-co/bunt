import logging

import boto3
import click
import pandas as pd

table = boto3.resource('dynamodb').Table('PRODUCTS')


def create_dynamo_object(row):
    return {
        'product_id': {'S': str(row['product_id'])},
        'red': {'S': row['red']},
        'green': {'S': row['green']},
        'blue': {'S': row['blue']},
    }


@click.command()
@click.option('--products-path', default='.', help='File path where the serialized object with products can be found')
def upload(products_path):
    dataset = pd.read_parquet(products_path)
    for i, row in dataset.iterrows():
        logging.info(f"Putting {row['product_id']}")
        try:
            table.update_item(
                Key={
                    'product_id': row['product_id'],
                },
                UpdateExpression="set Color.Red = :red and set Blue = :blue",
                ExpressionAttributeValues={
                    ':red': row['red'],
                    ':blue': row['blue'],
                },
                ReturnValues="UPDATED_NEW"
            )
        except Exception as e:
            logging.warning(e)
            pass


if __name__ == '__main__':
    upload()
