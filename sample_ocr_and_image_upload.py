import io
import os

from google.cloud import vision
from google.cloud import storage

#set temporary google credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'PATH_TO_JSON_CREDENTIALS'

def upload_image(path, bucket_name, remove_file = False):
    """
    Uploads image to the bucket, returns path to this image
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    filename = "image.png" #to be customized
    blob = bucket.blob(filename)
    with open(path, 'rb') as f:
        blob.upload_from_file(f)

    #remove image from the instance
    if remove_file:
        os.remove(path)
    return f"https://storage.cloud.google.com/{bucket_name}/{filename}"


def detect_text(path):
    """
    Detects text in the file.
    """

    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    text = texts[0].description
    text = text.replace("\n", " ")
    return text


if __name__ == '__main__':
    text = detect_text('./Memedroid/memedroid_2020041915_00003.jpeg')
    image_path = upload_image('./Memedroid/memedroid_2020041915_00003.jpeg',  'test_export_image')
    print(text)
