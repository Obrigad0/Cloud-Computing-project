import cv2
import io
import os
import glob
import random
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image
from common import validate_image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "detector.tflite")


def get_emoji_paths():
    """Trova tutti i PNG nella cartella dello script."""
    return glob.glob(os.path.join(SCRIPT_DIR, "*.png"))


def apply_random_emoji(image, detection_result) -> np.ndarray:
    """Applica un'emoji PNG casuale su ogni volto rilevato."""
    emoji_paths = get_emoji_paths()
    if not emoji_paths:
        raise FileNotFoundError("Nessun file .png trovato nella cartella dello script.")

    base_img = Image.fromarray(image).convert("RGBA")

    for detection in detection_result.detections:
        bbox = detection.bounding_box
        x, y, w, h = bbox.origin_x, bbox.origin_y, bbox.width, bbox.height

        scale_factor = 1.15
        new_w = max(1, int(w * scale_factor))
        new_h = max(1, int(h * scale_factor))

        offset_x = x - (new_w - w) // 2
        offset_y = y - (new_h - h) // 2

        emoji_path = random.choice(emoji_paths)
        emoji = Image.open(emoji_path).convert("RGBA")
        emoji_resized = emoji.resize((new_w, new_h), Image.LANCZOS)

        overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
        overlay.paste(emoji_resized, (offset_x, offset_y), emoji_resized)

        base_img = Image.alpha_composite(base_img, overlay)

    return np.array(base_img.convert("RGB"))


def analyze_img(file_bytes: bytes):
    err = validate_image(file_bytes)
    if err:
        return err

    # Salva temporaneamente su /tmp
    tmp_path = "/tmp/input_image.jpg"
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.FaceDetectorOptions(base_options=base_options)
    detector = vision.FaceDetector.create_from_options(options)

    image = mp.Image.create_from_file(tmp_path)
    detection_result = detector.detect(image)

    image_copy = np.copy(image.numpy_view())
    annotated_image = apply_random_emoji(image_copy, detection_result)

    output_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode(".jpg", output_bgr)
    return buffer.tobytes()
