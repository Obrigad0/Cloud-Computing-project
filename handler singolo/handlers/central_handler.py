import json

import boto3
from botocore.exceptions import ClientError

import modello as md
import flip as fl
import resize as rs
import grayscale as gs
import blur as bl
import blackWhite as bw

from common import validate_image, write_output, ok_response, error_response

# INPUT_BUCKET = "model-processing-images-input"
INPUT_BUCKET = "input-bucket-093678883134-us-east-1-an"

# DESTINATION_BUCKET = "model-processing-images-output"
DESTINATION_BUCKET = "output-bucket-093678883134-us-east-1-an"

OUTPUT_KEYS = {
    "flip": "flip_output.jpg",
    "grayscale": "grayscale_output.jpg",
    "process": "process_output.jpg",
    "blur": "blur_output.jpg",
    "resize": "resize_output.jpg",
    "blackwhite": "blackwhite_output.jpg",
}

s3 = boto3.client('s3')


def lambda_handler(event, context):
    # --- Parsing del body ---
    try:
        body = json.loads(event.get('body') or '{}')
    except (json.JSONDecodeError, TypeError):
        return error_response(400, 'Il body della richiesta non è un JSON valido')

    function_key = body.get('function_key')
    if not function_key or function_key not in OUTPUT_KEYS:
        return error_response(400, 'Campo "function_key" mancante o non valido nel body della richiesta')

    image_key = body.get('image_key')
    if not image_key:
        return error_response(400, 'Campo "image_key" mancante nel body della richiesta')

    # --- Lettura dell'immagine da S3 ---
    try:
        img_obj = s3.get_object(Bucket=INPUT_BUCKET, Key=image_key)
        img = img_obj['Body'].read()
    except ClientError as e:
        code = e.response.get('Error', {}).get('Code', '')
        if code in ('NoSuchKey', '404'):
            return error_response(404, f'Immagine "{image_key}" non trovata nel bucket di input')
        return error_response(500, 'Errore durante la lettura da S3', code)

    # --- Validazione (una volta sola) ---
    err = validate_image(img)
    if err:
        return err

    # --- Elaborazione: ogni funzione ritorna sempre bytes o solleva ---
    try:
        match function_key:
            case "process":
                returned_image = md.analyze_img(img)
            case "flip":
                returned_image = fl.flip_img(img)
            case "grayscale":
                returned_image = gs.grayscale_img(img)
            case "blackwhite":
                returned_image = bw.bW_img(img)
            case "blur":
                returned_image = bl.blur_img(img)
            case "resize":
                returned_image = rs.resize_img(img)
    except Exception as e:
        return error_response(500, "Errore durante l'elaborazione dell'immagine", e)

    # --- Scrittura dell'output (chiave fissa per funzione) ---
    output_key = function_key + "/" + OUTPUT_KEYS[function_key]
    err = write_output(returned_image, DESTINATION_BUCKET, output_key)
    if err:
        return err

    return ok_response({'function': function_key})
