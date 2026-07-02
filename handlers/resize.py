import cv2
import io
import numpy as np
import mediapipe as mp
import random as rm
from PIL import Image

MIN_SIZE = 100
MAX_SIZE = 1920

def resize_img(file_bytes: bytes):
    # Verifica che sia un'immagine
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
    except (IOError, SyntaxError) as e:
        return False

    # Salva temporaneamente su /tmp (unico path scrivibile in Lambda)
    tmp_path = "/tmp/input_image.jpg"
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    img = mp.Image.create_from_file(tmp_path)
    image_copy = np.copy(img.numpy_view())  # formato RGB
    image_copy = cv2.cvtColor(image_copy, cv2.COLOR_RGB2BGR)

    new_height = rm.randint(MIN_SIZE, MAX_SIZE)
    new_width = rm.randint(MIN_SIZE, MAX_SIZE)

    scaled_image = cv2.resize(image_copy, (new_width, new_height), cv2.INTER_LINEAR)

    # Converti in bytes per S3
    _, buffer = cv2.imencode(".jpg", scaled_image)
    return buffer.tobytes()