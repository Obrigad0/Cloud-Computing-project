import modello as md
import boto3
import botocore

BUCKET_INPUT = 'amzn-s3-demo-bucket'
REGION = 'us-west-1'

def getInputs():
    s3 = boto3.resource('s3')
    
    bucket = s3.Bucket(BUCKET_INPUT)
    exists = True
    try:
        s3.meta.client.head_bucket(Bucket=BUCKET_INPUT)
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = e.response['Error']['Code']
        if error_code == '404':
            exists = False

    # Per iterare in vari buckets
    for bucket in s3.buckets.all():
        for key in bucket.objects.all():
            print(key.key)

getInputs()
