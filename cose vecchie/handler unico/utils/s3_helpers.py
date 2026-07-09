# utils/s3_helpers.py
import boto3
import io

s3 = boto3.client("s3")

def download_image(bucket: str, key: str) -> bytes:
    resp = s3.get_object(Bucket=bucket, Key=key)
    return resp["Body"].read()

def upload_image(bucket: str, key: str, image_bytes: bytes, content_type: str = "image/jpeg"):
    s3.put_object(Bucket=bucket, Key=key, Body=image_bytes, ContentType=content_type)