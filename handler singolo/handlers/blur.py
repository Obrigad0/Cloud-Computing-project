import cv2
import numpy as np
import mediapipe as mp

from common import validate_image

BLUR_SIZE = (30, 30)


def blur_img(file_bytes: bytes):
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
        blur_image = cv2.blur(image_copy, BLUR_SIZE)

        _, buffer = cv2.imencode(".jpg", blur_image)
    except Exception as e:
        return e
    return buffer.tobytes()
