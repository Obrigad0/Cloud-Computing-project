import cv2
import numpy as np
import mediapipe as mp

from common import get_input_image, validate_image, write_output, ok_response, error_response

INPUT_BUCKET = "model-processing-images-input"
DESTINATION_BUCKET = "output-bucket-093678883134-us-east-1-an"
OUTPUT_KEY = "blackwhite_output.jpg"


def lambda_handler(event, context):
    image_bytes, err = get_input_image(event, INPUT_BUCKET)
    if err:
        return err

    err = validate_image(image_bytes)
    if err:
        return err

    try:
        tmp_path = "/tmp/input_image.jpg"
        with open(tmp_path, "wb") as f:
            f.write(image_bytes)

        img = mp.Image.create_from_file(tmp_path)
        image_copy = np.copy(img.numpy_view())
        gray_image = cv2.cvtColor(image_copy, cv2.COLOR_RGB2GRAY)
        bW_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)[1]

        _, buffer = cv2.imencode(".jpg", bW_image)
    except Exception as e:
        return error_response(500, "Errore durante l'elaborazione dell'immagine", e)

    err = write_output(buffer.tobytes(), DESTINATION_BUCKET, OUTPUT_KEY)
    if err:
        return err

    return ok_response({'function': 'blackwhite'})
