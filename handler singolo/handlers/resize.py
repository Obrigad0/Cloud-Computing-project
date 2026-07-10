import cv2
import numpy as np
import mediapipe as mp
import random as rm

MIN_SIZE = 100
MAX_SIZE = 1920


def resize_img(file_bytes: bytes) -> bytes:
    tmp_path = "/tmp/input_image.jpg"
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    img = mp.Image.create_from_file(tmp_path)
    image_copy = np.copy(img.numpy_view())
    image_copy = cv2.cvtColor(image_copy, cv2.COLOR_RGB2BGR)

    new_height = rm.randint(MIN_SIZE, MAX_SIZE)
    new_width = rm.randint(MIN_SIZE, MAX_SIZE)

    scaled_image = cv2.resize(image_copy, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    _, buffer = cv2.imencode(".jpg", scaled_image)
    return buffer.tobytes()
