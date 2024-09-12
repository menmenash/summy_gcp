"""
DynamoDB Manager

This module contains the DynamoDBManager class, which is responsible for managing
interactions with Amazon DynamoDB.

Classes:
    DynamoDBManager: Manages DynamoDB operations.

Methods:
    __init__(self, table_name: str, region_name: str = 'eu-north-1'):
        Initializes the DynamoDBManager with a table name and region.

    create_table_if_not_exists(self):
        Creates the DynamoDB table if it doesn't already exist.

    get_item(self, key: str):
        Retrieves an item from the DynamoDB table.

    put_item(self, key: str, value: str):
        Puts an item into the DynamoDB table.

Attributes:
    table_name (str): The name of the DynamoDB table.
    dynamodb (boto3.resource): The DynamoDB resource.
    dynamodb_client (boto3.client): The DynamoDB client.
    table (boto3.Table): The DynamoDB table object.

Note:
    This class requires appropriate AWS credentials to function properly.
"""

import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class DynamoDBManager:
    def __init__(self, table_name: str, region_name: str = 'eu-north-1'):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.dynamodb_client = boto3.client('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(self.table_name)
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        try:
            self.dynamodb_client.describe_table(TableName=self.table_name)
            logger.info(f"Table {self.table_name} already exists.")
        except self.dynamodb_client.exceptions.ResourceNotFoundException:
            logger.info(f"Creating table {self.table_name}...")
            self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'config_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'config_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            self.table.wait_until_exists()
            logger.info(f"Table {self.table_name} created successfully.")

    def get_item(self, key: str):
        try:
            response = self.table.get_item(Key={'config_id': key})
            return response.get('Item', {}).get('value')
        except ClientError as e:
            logger.error(f"Error getting item from DynamoDB: {e}")
            return None

    def put_item(self, key: str, value: str):
        try:
            self.table.put_item(Item={'config_id': key, 'value': value})
            return True
        except ClientError as e:
            logger.error(f"Error putting item in DynamoDB: {e}")
            return False