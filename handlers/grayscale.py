from PIL import Image
import io
from utils.s3_helpers import download_image, upload_image

def lambda_handler(event, context):
    img_bytes = download_image(event["source_bucket"], event["source_key"])
    with Image.open(io.BytesIO(img_bytes)) as img:
        grayscale = img.convert("L")
        out = io.BytesIO()
        grayscale.save(out, format=img.format or "JPEG")
    upload_image(event["dest_bucket"], event["dest_key"], out.getvalue())
    return {"statusCode": 200, "body": f"Grayscale salvato → {event['dest_key']}"}