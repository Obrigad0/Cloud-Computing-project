from . import modello as md
from . import grayscale as gs
from . import flip as fl
import boto3
import json

INPUT_DIRS = ["process", "flip", "grayscale"]
DESTINATION_BUCKET = "model-processing-images-output"
s3 = boto3.client('s3')


def lambda_handler(event, context):
    print((event))
    for record in event['Records']:
        #Recupera l'immagine dal bucket
        bucket_input = record['s3']['bucket']['name']
        input_key = record['s3']['object']['key']
        img_obj = s3.get_object(Bucket=bucket_input, Key=input_key)
        img = img_obj['Body'].read()

        # In base al bucket di provenienza, sceglie l'operazione collegata
        input_dir = input_key.split('/')[0]
        op_code = INPUT_DIRS.index(input_dir)
        returned_image = None
        
        match op_code:
            case 0: # Chiama la funzione per rilevare le facce nell'immagine
                returned_image = md.analyze_img(img)
            case 1:
                returned_image = fl.flip_img(img)
            case 2: # Chiama la funzione per trasformare l'immagine in bianco e nero
                returned_image = gs.grayscale_img(img)

        if returned_image == False or returned_image == None:
            return 
            {
                'statusCode': 400,
                'body': 'The uploaded file was not an image'
            }   
        
        s3.put_object(
            Bucket=DESTINATION_BUCKET,
            Key=input_key,
            Body=returned_image,
            ContentType='image/jpeg'   # <-- 'image' da solo non è un mimetype valido
        )
    return {'statusCode': 200}
