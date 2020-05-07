import sys
from io import BytesIO
import json
from google.cloud import vision
from google.protobuf.json_format import MessageToDict


if __name__ == "__main__":
	
	os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./GCP-cred.json"

    client = vision.ImageAnnotatorClient()

    # load image
    content = sys.stdin.buffer.read()
    image = vision.types.Image(content=content)

    # OCR on image
    response = client.text_detection(image=image)
    response_dict = MessageToDict(response)
    image_text = response_dict.get('textAnnotations', [{}])[0].get('description', '')
    image_text = image_text.replace('\n', ' ')

    # Return OCR text
    print(json.dumps({"text": image_text}))
