import cv2
import numpy as np
import mediapipe as mp

from common import validate_image, write_output, ok_response, error_response

INPUT_BUCKET = "model-processing-images-input"
DESTINATION_BUCKET = "model-processing-images-output"
OUTPUT_KEY = "flip_output.jpg"


def flip_img(file_bytes: bytes):
    err = validate_image(file_bytes)
    if err:
        return err

    try:
        tmp_path = "/tmp/input_image.jpg"
        with open(tmp_path, "wb") as f:
            f.write(file_bytes)

        img = mp.Image.create_from_file(tmp_path)
        image_copy = np.copy(img.numpy_view())
        image_copy = cv2.cvtColor(image_copy, cv2.COLOR_RGB2BGR)
        flip_img = cv2.flip(image_copy, 1)

        _, buffer = cv2.imencode(".jpg", flip_img)
    except Exception as e:
        return e
    return buffer.tobytes()