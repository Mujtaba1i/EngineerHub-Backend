import os
from dotenv import load_dotenv

load_dotenv()

db_URI = os.getenv('DATABASE_URL')
secret = os.getenv('JWT_SECRET')

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION', 'us-east-1')
s3_bucket_name = os.getenv('S3_BUCKET_NAME', 'engineerhub-notes')