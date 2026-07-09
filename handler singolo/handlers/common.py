"""
Funzioni di supporto condivise da tutti gli handler Lambda esposti tramite API Gateway.
Gestiscono il parsing della richiesta JSON, il recupero dell'immagine da S3,
la validazione e la costruzione delle risposte in formato Lambda proxy integration.
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


def get_input_image(event, input_bucket):
    """
    Legge 'image_key' dal body JSON della richiesta e scarica il file corrispondente
    dal bucket di input.

    Ritorna:
        (image_bytes, None) in caso di successo
        (None, error_response) in caso di errore (400/404/500 già pronto da restituire)
    """
    try:
        body = json.loads(event.get('body') or '{}')
    except (json.JSONDecodeError, TypeError):
        return None, error_response(400, 'Il body della richiesta non è un JSON valido')

    image_key = body.get('image_key')
    if not image_key:
        return None, error_response(400, 'Campo "image_key" mancante nel body della richiesta')

    try:
        img_obj = s3.get_object(Bucket=input_bucket, Key=image_key)
        return img_obj['Body'].read(), None
    except ClientError as e:
        code = e.response.get('Error', {}).get('Code', '')
        if code in ('NoSuchKey', '404'):
            return None, error_response(404, f'Immagine "{image_key}" non trovata nel bucket di input')
        return None, error_response(500, 'Errore durante la lettura da S3', code)


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
    Scrive l'immagine elaborata nel bucket di output (chiave fissa, sovrascritta
    ad ogni richiesta: non serve tracciare il singolo output per richiesta).

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
