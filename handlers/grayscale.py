import cv2
import io
import numpy as np
import mediapipe as mp
from PIL import Image

def grayscale_img(file_bytes : bytes): 
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
    gray_image = cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB)    

    # Converti in bytes per S3
    _, buffer = cv2.imencode(".jpg", gray_image)
    return buffer.tobytes()

"""
def lambda_handler(event, context):
    img_bytes = download_image(event["source_bucket"], event["source_key"])
    with Image.open(io.BytesIO(img_bytes)) as img:
        grayscale = img.convert("L")
        out = io.BytesIO()
        grayscale.save(out, format=img.format or "JPEG")
    upload_image(event["dest_bucket"], event["dest_key"], out.getvalue())
    return {"statusCode": 200, "body": f"Grayscale salvato → {event['dest_key']}"}
"""