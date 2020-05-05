import sys
import os
import json
import urllib.request
import datetime
import re
import pathlib


def time():
    return datetime.datetime.now().strftime("%Y%m%d%H")


def time_extended():
    return datetime.datetime.utcnow().strftime('%Y.%m.%d, %H:%M')


if __name__ == "__main__":
    data = json.loads(sys.stdin.read())
    images_data = [
        image_data for image_dataset in data for image_data in image_dataset]
    current_time = time()

    log = []

    for i, image_data in enumerate(images_data):
        image_url = image_data["url"]
        try:
            image_extension = re.split(
                r'[^\w]', image_url.split('/')[-1].split('.')[1])[0]
        except KeyError:
            image_extension = "png"
            log.append(
                f"{time_extended()}: Failed to resolve {image_url} extension, png chosen.")
        image_source = image_data["source"]
        image_filename = f"{image_source}_{current_time}_{i:05}.{image_extension}"

        directory_path = f"../images/{image_source}"
        pathlib.Path(directory_path).mkdir(parents=True, exist_ok=True)
        image_path = os.path.join(directory_path, image_filename)
        urllib.request.urlretrieve(image_url, image_path)

        image_data['text'] = f"Tekst {i}"
        log.append(
            f"{time_extended()}: Image {image_url} downloaded to {image_path}.")

    directory_path = f"../logs/"
    pathlib.Path(directory_path).mkdir(parents=True, exist_ok=True)
    log_path = os.path.join(directory_path, f"process_ocr_{current_time}.log")
    log = "\n".join(log) + "\n"
    with open(log_path, 'a') as file_:
        file_.write(log)

    with open('output.txt', 'w') as f:
        f.write(json.dumps(images_data, indent=4))
