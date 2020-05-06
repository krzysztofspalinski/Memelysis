import sys
from io import BytesIO

if __name__ == "__main__":
    image = Image.open(BytesIO(sys.stdin.buffer.read()))
    image.save(f"img.{image.format}", "w")

    # OCR on image

    print(image)
