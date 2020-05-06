import sys
from io import BytesIO
from PIL import Image

if __name__ == "__main__":
    image = Image.open(BytesIO(sys.stdin.buffer.read()))
    image.save(f"img.{image.format}")

    # OCR on image
    text = "Text from image"

    print(text)
