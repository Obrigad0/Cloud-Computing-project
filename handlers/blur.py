from PIL import Image, ImageFilter
import io
from utils.s3_helpers import download_image, upload_image

"""
def lambda_handler(event, context):
    radius    = float(event.get("radius", 2.0))
    img_bytes = download_image(event["source_bucket"], event["source_key"])
    with Image.open(io.BytesIO(img_bytes)) as img:
        result = img.filter(ImageFilter.GaussianBlur(radius=radius))
        out = io.BytesIO()
        result.save(out, format=img.format or "JPEG")
    upload_image(event["dest_bucket"], event["dest_key"], out.getvalue())
    return {"statusCode": 200, "body": f"Blur radius={radius} → {event['dest_key']}"}"""