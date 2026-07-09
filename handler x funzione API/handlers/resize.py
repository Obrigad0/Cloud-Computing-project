import cv2
import numpy as np
import mediapipe as mp
import random as rm

from common import get_input_image, validate_image, write_output, ok_response, error_response

MIN_SIZE = 100
MAX_SIZE = 1920
INPUT_BUCKET = "model-processing-images-input"
DESTINATION_BUCKET = "model-processing-images-output"
OUTPUT_KEY = "resize_output.jpg"


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
        image_copy = cv2.cvtColor(image_copy, cv2.COLOR_RGB2BGR)

        new_height = rm.randint(MIN_SIZE, MAX_SIZE)
        new_width = rm.randint(MIN_SIZE, MAX_SIZE)

        scaled_image = cv2.resize(image_copy, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        _, buffer = cv2.imencode(".jpg", scaled_image)
    except Exception as e:
        return error_response(500, "Errore durante l'elaborazione dell'immagine", e)

    err = write_output(buffer.tobytes(), DESTINATION_BUCKET, OUTPUT_KEY)
    if err:
        return err

    return ok_response({'function': 'resize'})
