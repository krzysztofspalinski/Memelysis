import sys
from io import BytesIO
from PIL import Image
import json

if __name__ == "__main__":
    image = Image.open(BytesIO(sys.stdin.buffer.read()))
    image.save(f"img.{image.format}")

    # OCR on image
    image_text = "Text from image"

    print(json.dumps({"text": image_text}))
