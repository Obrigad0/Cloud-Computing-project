import modello as md
import flip as fl
import resize as rs
import grayscale as gs
import blur as bl
import blackWhite as bw

import json

import boto3
from botocore.exceptions import ClientError

from common import write_output, ok_response, error_response

INPUT_BUCKET = "model-processing-images-input"

DESTINATION_BUCKET = "model-processing-images-output"

OUTPUT_KEYS = {"flip": "flip_output.jpg", 
"grayscale": "grayscale_output.jpg", 
"process": "process_output.jpg", 
"blur" : "blur_output.jpg",
"resize" : "resize_output.jpg", 
"blackwhite" : "blackwhite_output.jpg"}

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body') or '{}')
    except (json.JSONDecodeError, TypeError):
        return None, error_response(400, 'Il body della richiesta non è un JSON valido')

    function_key = body.get('function_key')
    if not function_key:
        return None, error_response(400, 'Campo "function_key" mancante nel body della richiesta')
    
    image_key = body.get("image_key")
    if not image_key:
        return None, error_response(400, 'Campo "image_key" mancante nel body della richiesta')
    
    img = None
    
    try:
        img_obj = s3.get_object(Bucket=INPUT_BUCKET, Key=image_key)
        img = img_obj['Body'].read(), None
    
    except ClientError as e:
        code = e.response.get('Error', {}).get('Code', '')
        if code in ('NoSuchKey', '404'):
            return None, error_response(404, f'Immagine "{image_key}" non trovata nel bucket di input')
        return None, error_response(500, 'Errore durante la lettura da S3', code)

    returned_image = None
    match function_key:
        case "process": # Chiama la funzione per rilevare le facce nell'immagine
            returned_image = md.analyze_img(img)
        case "flip": # Chiama la funzione per ribaltare l'immagine
            returned_image = fl.flip_img(img)
        case "grayscale": # Chiama la funzione per trasformare l'immagine in scala di grigi
            returned_image = gs.grayscale_img(img)
        case "blackwhite": # Chiama la funzione per trasformare l'immagine in bianco e nero
            returned_image = bw.bW_img(img)
        case "blur": # Chiama la funzione per sfocare l'immagine
            returned_image = bl.blur_img(img)
        case "resize": # Chiama la funzione per ridimensionare (casualmente) l'immagine
            returned_image = rs.resize_img(img)

    if returned_image is False or returned_image is Exception:
        return error_response(400, "Il file richiesto non è un'immagine valida")

    err = write_output(returned_image, DESTINATION_BUCKET, OUTPUT_KEYS[function_key])
    
    if err: return err

    return ok_response({'function': 'process'})
