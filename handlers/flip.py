import cv2
import io
import numpy as np
import mediapipe as mp
from PIL import Image

def flip_img(file_bytes : bytes):
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
    image_copy = np.copy(img.numpy_view())
    flip_img = cv2.flip(image_copy, 1)

    # Converti in bytes per S3
    _, buffer = cv2.imencode(".jpg", flip_img)
    return buffer.tobytes()
