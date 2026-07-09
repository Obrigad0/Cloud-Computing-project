import modello as md

from common import get_input_image, write_output, ok_response, error_response

INPUT_BUCKET = "model-processing-images-input"
DESTINATION_BUCKET = "output-bucket-093678883134-us-east-1-an"
OUTPUT_KEY = "process_output.jpg"


def lambda_handler(event, context):
    image_bytes, err = get_input_image(event, INPUT_BUCKET)
    if err:
        return err

    # analyze_img fa già la validazione dell'immagine e ritorna False se non valida
    try:
        analyzed_image = md.analyze_img(image_bytes)
    except Exception as e:
        return error_response(500, "Errore durante l'elaborazione dell'immagine", e)

    if analyzed_image is False:
        return error_response(400, "Il file richiesto non è un'immagine valida")

    err = write_output(analyzed_image, DESTINATION_BUCKET, OUTPUT_KEY)
    if err:
        return err

    return ok_response({'function': 'process'})
