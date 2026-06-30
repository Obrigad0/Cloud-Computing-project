from PIL import Image
import io
from utils.s3_helpers import download_image, upload_image

def lambda_handler(event, context):
    angle      = float(event["angle"])
    expand     = event.get("expand", True)
    fill_color = event.get("fill_color", "black")
    img_bytes  = download_image(event["source_bucket"], event["source_key"])
    with Image.open(io.BytesIO(img_bytes)) as img:
        result = img.rotate(angle, expand=expand, fillcolor=fill_color, resample=Image.BICUBIC)
        out = io.BytesIO()
        result.save(out, format=img.format or "JPEG")
    upload_image(event["dest_bucket"], event["dest_key"], out.getvalue())
    return {"statusCode": 200, "body": f"Rotazione {angle}° → {event['dest_key']}"}