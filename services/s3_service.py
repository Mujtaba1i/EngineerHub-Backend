import boto3
from botocore.exceptions import ClientError
from config.environment import (aws_access_key_id,aws_secret_access_key,aws_region,s3_bucket_name)
import uuid
from datetime import datetime

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        self.bucket_name = s3_bucket_name
    
    def upload_file(self, file_content, file_name, content_type):
        """
        Upload a file to S3 bucket
        Returns the file key (path in S3)
        """
        try:
            # Generate unique filename with timestamp
            file_extension = file_name.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}_{datetime.now().timestamp()}.{file_extension}"
            file_key = f"notes/{unique_filename}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                # Make file private (not public)
                ACL='private'
            )
            
            return file_key
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def generate_presigned_url(self, file_key, expiration=3600):
        """
        Generate a presigned URL for downloading a file
        Default expiration is 1 hour (3600 seconds)
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            raise Exception(f"Failed to generate download URL: {str(e)}")
    
    def delete_file(self, file_key):
        """
        Delete a file from S3 bucket
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            raise Exception(f"Failed to delete file: {str(e)}")
    
    def get_file_metadata(self, file_key):
        """
        Get metadata of a file in S3
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return {
                'size': response['ContentLength'],
                'content_type': response['ContentType'],
                'last_modified': response['LastModified']
            }
        except ClientError as e:
            print(f"Error getting file metadata: {e}")
            raise Exception(f"Failed to get file metadata: {str(e)}")

# Create singleton instance
s3_service = S3Service()