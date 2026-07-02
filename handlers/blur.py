import cv2
import io
import numpy as np
import mediapipe as mp
from PIL import Image

BLUR_SIZE = (30,30)

def blur_img(file_bytes : bytes):
    # Verifica che sia un'immagine
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
    except (IOError, SyntaxError):
        return False

    # Salva temporaneamente su /tmp (unico path scrivibile in Lambda)
    tmp_path = "/tmp/input_image.jpg"
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    img = mp.Image.create_from_file(tmp_path)
    image_copy = np.copy(img.numpy_view())  # formato RGB
    blur_image = cv2.blur(image_copy, BLUR_SIZE) 

    # Converti in bytes per S3
    _, buffer = cv2.imencode(".jpg", blur_image)
    return buffer.tobytes()