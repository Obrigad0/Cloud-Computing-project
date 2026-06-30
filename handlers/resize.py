from PIL import Image
import io
from utils.s3_helpers import download_image, upload_image

def lambda_handler(event, context):
    width      = int(event["width"])
    height     = int(event["height"])
    keep_ratio = event.get("keep_ratio", False)
    img_bytes  = download_image(event["source_bucket"], event["source_key"])
    with Image.open(io.BytesIO(img_bytes)) as img:
        if keep_ratio:
            img.thumbnail((width, height), Image.LANCZOS)
            result = img
        else:
            result = img.resize((width, height), Image.LANCZOS)
        out = io.BytesIO()
        result.save(out, format=img.format or "JPEG")
    upload_image(event["dest_bucket"], event["dest_key"], out.getvalue())
    return {"statusCode": 200, "body": f"Resize {width}x{height} → {event['dest_key']}"}