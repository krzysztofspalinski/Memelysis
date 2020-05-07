import sys
from io import BytesIO
from PIL import Image
import json

if __name__ == "__main__":
    
    # load image
    content = BytesIO(sys.stdin.buffer.read())
    image = vision.types.Image(content=content)

    # OCR on image
    response = client.text_detection(image=image)
    image_text = response_dict['textAnnotations'][0]['description']
    image_text = image_text.replace('\n', ' ')

    # Return OCR text
    print(json.dumps({"text": image_text}))
