"""
Funzioni di supporto condivise dagli handler Lambda esposti tramite API Gateway.
Gestiscono la validazione dell'immagine, la scrittura su S3 e la costruzione
delle risposte nel formato Lambda proxy integration.
"""
import json
from io import BytesIO

import boto3
from PIL import Image
from botocore.exceptions import ClientError

s3 = boto3.client('s3')


def json_response(status_code, body_dict):
    """Costruisce una risposta nel formato richiesto da API Gateway (proxy integration)."""
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body_dict)
    }


def ok_response(extra=None):
    body = {'message': 'ok'}
    if extra:
        body.update(extra)
    return json_response(200, body)


def error_response(status_code, message, detail=None):
    body = {'error': message}
    if detail is not None:
        body['detail'] = str(detail)
    return json_response(status_code, body)


def validate_image(image_bytes):
    """Ritorna None se image_bytes è un'immagine valida, altrimenti una error_response 400."""
    try:
        with Image.open(BytesIO(image_bytes)) as img:
            img.verify()
        return None
    except (IOError, SyntaxError):
        return error_response(400, "Il file richiesto non è un'immagine valida")


def write_output(image_bytes, destination_bucket, output_key):
    """
    Scrive l'immagine elaborata nel bucket di output (chiave fissa per funzione,
    sovrascritta ad ogni richiesta: non serve tracciare il singolo output per richiesta).

    Ritorna None in caso di successo, altrimenti una error_response 500.
    """
    try:
        s3.put_object(
            Bucket=destination_bucket,
            Key=output_key,
            Body=image_bytes,
            ContentType='image/jpeg'
        )
        return None
    except ClientError as e:
        return error_response(500, 'Errore durante la scrittura su S3', str(e))
