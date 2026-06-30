from PIL import Image
import io
from utils.s3_helpers import download_image, upload_image

FLIP_MAP = {
    "horizontal": Image.FLIP_LEFT_RIGHT,
    "vertical":   Image.FLIP_TOP_BOTTOM,
}
"""
def lambda_handler(event, context):
    direction = event.get("direction", "horizontal").lower()
    img_bytes = download_image(event["source_bucket"], event["source_key"])
    with Image.open(io.BytesIO(img_bytes)) as img:
        if direction == "both":
            result = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
        elif direction in FLIP_MAP:
            result = img.transpose(FLIP_MAP[direction])
        else:
            return {"statusCode": 400, "body": f"direction non valida: '{direction}'"}
        out = io.BytesIO()
        result.save(out, format=img.format or "JPEG")
    upload_image(event["dest_bucket"], event["dest_key"], out.getvalue())
    return {"statusCode": 200, "body": f"Flip '{direction}' salvato → {event['dest_key']}"}
"""