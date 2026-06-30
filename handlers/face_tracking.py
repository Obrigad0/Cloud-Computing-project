import modello as md
import json
import boto3

DESTINATION_BUCKET = "output-images"
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    bucket_input = event['Records'][0]['s3']['bucket']['name']
    input_key = event['Records'][0]['s3']['object']['key']
    
    img_obj = s3.get_object(Bucket=bucket_input, Key=input_key)
    img = img_obj['Body'].read()

    returned_image = md.analyze_img(img)
    if returned_image == False:
        return {
            'statusCode': 400,
            'body': 'The uploaded file was not an image'
        }
        
    s3.put_object(
        Bucket= DESTINATION_BUCKET,
        Key= input_key,
        Body= returned_image,
        ContentType='image'
    )

    return {'statusCode': 200}
