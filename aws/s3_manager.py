"""
S3 Manager

This module contains the S3Manager class, which is responsible for managing
interactions with Amazon S3.

Classes:
    S3Manager: Manages S3 operations.

Methods:
    __init__(self, s3_client, bucket_name: str):
        Initializes the S3Manager with an S3 client and bucket name.

    store_article(self, article_text: str):
        Stores an article text in the S3 bucket.

    retrieve_article(self) -> str:
        Retrieves the last stored article from the S3 bucket.

Attributes:
    s3_client (boto3.client): The S3 client used for operations.
    bucket_name (str): The name of the S3 bucket.

Note:
    This class requires appropriate AWS credentials to function properly.
"""

from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class S3Manager:
    def __init__(self, s3_client, bucket_name: str):
        self.s3_client = s3_client
        self.bucket_name = bucket_name

    def store_article(self, article_text: str):
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key='Last_Article', Body=article_text.encode('utf-8'))
            logger.info("Article stored successfully in S3.")
        except ClientError as e:
            logger.error(f"Failed to store article in S3: {str(e)}")

    def retrieve_article(self) -> str:
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key='Last_Article')
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            logger.error(f"Failed to retrieve article from S3: {str(e)}")
            return ""