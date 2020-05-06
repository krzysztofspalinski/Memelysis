import sys
import os
import json
import urllib.request
import datetime
import pathlib

if __name__ == "__main__":
    data = json.loads(sys.stdin.read())
    images_data = [
        image_data for image_dataset in data for image_data in image_dataset]

    print(json.dumps(images_data, indent=4))
