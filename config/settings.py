"""
Project settings
"""
import os
from pathlib import Path
import boto3

from dotenv import load_dotenv

load_dotenv()

CLIENT_BOT_TOKEN = os.getenv('CLIENT_BOT_TOKEN')
MASTER_BOT_TOKEN = os.getenv('MASTER_BOT_TOKEN')
ORGANIZATION_BOT_TOKEN = os.getenv('ORGANIZATION_BOT_TOKEN')
MODERATOR_BOT_TOKEN = os.getenv('MODERATOR_BOT_TOKEN')

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
AWS_UPLOAD_URL = os.getenv('AWS_UPLOAD_URL')
AWS_CUSTOM_URL = os.getenv('AWS_CUSTOM_URL')

bucket_name = AWS_BUCKET_NAME

session = boto3.Session(
    aws_access_key_id=(AWS_ACCESS_KEY),
    aws_secret_access_key=(AWS_SECRET_KEY),
    region_name="ru-1",


)

s3 = session.client(
    "s3", endpoint_url=AWS_UPLOAD_URL)

