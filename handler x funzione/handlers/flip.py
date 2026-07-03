import cv2
import io
import numpy as np
import mediapipe as mp
import boto3
from PIL import Image

DESTINATION_BUCKET = "model-processing-images-output"
s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_input = event['Records'][0]['s3']['bucket']['name']
    input_key = event['Records'][0]['s3']['object']['key']

    img_obj = s3.get_object(Bucket=bucket_input, Key=input_key)
    image_bytes = img_obj['Body'].read()

    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img.verify()
    except (IOError, SyntaxError):
        return 
        {
            'statusCode': 400,
            'body': 'The uploaded file was not an image'
        }   

    # Salva temporaneamente su /tmp (unico path scrivibile in Lambda)
    tmp_path = "/tmp/input_image.jpg"
    with open(tmp_path, "wb") as f:
        f.write(image_bytes)

    img = mp.Image.create_from_file(tmp_path)
    image_copy = np.copy(img.numpy_view())
    image_copy = cv2.cvtColor(image_copy, cv2.COLOR_RGB2BGR)
    flip_img = cv2.flip(image_copy, 1)

    # Converti in bytes per S3
    _, buffer = cv2.imencode(".jpg", flip_img)
    
    # Carica l'immagine nel bucket di ritorno
    s3.put_object(
            Bucket=DESTINATION_BUCKET,
            Key=input_key,
            Body=buffer.tobytes(),
            ContentType='image/jpeg'   # <-- 'image' da solo non è un mimetype valido
        )
    return {'statusCode': 200}
