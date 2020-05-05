import sys
import json
import urllib.request
import datetime
import re


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
            image_extension = re.split(r'[^\w]', image_url.split('/')[-1])[0]
        except KeyError:
            image_extension = "png"
            log.append(
                f"{time_extended()}: Failed to resolve {image_url} extension, png chosen.")
        image_source = image_data["source"]
        image_filename = f"{source}_{current_time()}_{i:05}.{image_extension}"
        try:
            os.mkdir(source)
        except FileExistsError:
            pass
        finally:
            pass
        image_path = f"{source}/{image_filename}"
        urllib.request.urlretrieve(image_url, image_path)

        image_data['text'] = f"Tekst {i}"

    log.append(
        f"{time_extended()}: Image {image_url} downloaded to {image_path}.")

    log_path = os.path.join(sys.path[0], f'imgur_{current_time}.log')
    log = "\n".join(log) + "\n"
    with open(log_path, 'a') as file_:
        file_.write(log)
