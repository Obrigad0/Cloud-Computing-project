import boto3
from . import modello as md

INPUT_DIRS = ["process", "flip", "grayscale", "blackwhite", "blur", "resize"]
DESTINATION_BUCKET = "output-bucket-093678883134-us-east-1-an"
s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_input = event['Records'][0]['s3']['bucket']['name']
    input_key = event['Records'][0]['s3']['object']['key']

    img_obj = s3.get_object(Bucket=bucket_input, Key=input_key)
    image_bytes = img_obj['Body'].read()

    analyzed_image = md.analyze_img(image_bytes)


    # In caso di errori, lo ritorna
    if analyzed_image == False:
        return 
        {
            'statusCode': 400,
            'body': 'The uploaded file was not an image'
        }   
        
    s3.put_object(
            Bucket=DESTINATION_BUCKET,
            Key=input_key,
            Body=analyzed_image,
            ContentType='image/jpeg'   # <-- 'image' da solo non è un mimetype valido
        )
    return {'statusCode': 200}
