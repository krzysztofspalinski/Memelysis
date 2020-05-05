import json
import datetime
import sys
import os
import urllib
import requests
import pathlib
from credentials import AUTHORIZATION


def time():
    return datetime.datetime.now().strftime("%Y%m%d%H")


def time_extended():
    return datetime.datetime.utcnow().strftime('%Y.%m.%d, %H:%M')


def obtain_data_from_imgur(
        start_timestamp=None,
        end_timestamp=None,
        sort="time",
        page=0,
        window="day",
        temporary=False):
    """Obtains posts from imgur.com

    Args:
        sort (str, optional): viral | top | time | rising (only available with user section). Defaults to "time".
        page (int, optional): The data paging number. If is equal to -1, then it returns all available posts. Defaults to 0.
        window (str, optional): Change the date range of the request if the section is "top", day | week | month | year | all. Defaults to "day".

    Returns:
        dict: Posts in the gallery.
    """

    log = []

    if start_timestamp is not None or end_timestamp is not None:
        window = "all"

    start_timestamp = start_timestamp or float("-inf")
    end_timestamp = end_timestamp or float("inf")

    headers = {
        'Authorization': AUTHORIZATION,
    }

    max_attempts = 3
    posts = []

    # Obtain post list

    log.append(f"{time_extended()}: Obtaining data from imgur.")

    if int(page) != -1:
        attempts = 0
        while attempts < max_attempts:
            try:
                url = f'https://api.imgur.com/3/g/memes/{sort}/{window}/{page}'
                response = requests.get(url, headers=headers)
                posts = [post for post in response.json().get(
                    'data', []) if start_timestamp <= post["datetime"] < end_timestamp]
                break
            except requests.exceptions.ConnectionError:
                attempts += 1
            except TypeError:
                attempts += 1
    else:
        while True:
            page += 1
            attempts = 0
            more_posts = []
            while attempts < max_attempts:
                try:
                    url = f'https://api.imgur.com/3/g/memes/{sort}/{window}/{page}'
                    response = requests.get(url, headers=headers)
                    more_posts = [post for post in response.json().get(
                        'data', []) if start_timestamp <= post["datetime"] < end_timestamp]
                    posts.extend(more_posts)
                    break
                except requests.exceptions.ConnectionError:
                    attempts += 1
                except TypeError:
                    attempts += 1
            if len(more_posts) < 60:
                break

    posts = [post for post in posts if all("image" in image.get(
        "type", '') for image in post.get('images', []))]

    log.append(f'{time_extended()}: Found {len(posts)} memes to download.')

    # Format JSON

    images = []
    for post in posts:
        for image in post.get("images", []):
            image_url = image["link"]
            images.append({
                'url': image_url,
                'source': "imgur",
                'additional_data': post,
            })

    # Save log file

    if temporary is True:
        container_path = os.path.join(sys.path[0], "tmp")
    else:
        container_path = os.path.join(sys.path[0])

    directory_path = f"../../logs"
    pathlib.Path(directory_path).mkdir(parents=True, exist_ok=True)
    log_path = os.path.join(directory_path, f'imgur_{time()}.log')
    log = "\n".join(log) + "\n"
    with open(log_path, 'a') as file_:
        file_.write(log)

    return images


def main():
    """Obtains images from imgur.com
    """

    shift = 0
    data = obtain_data_from_imgur(
        page=-1,
        start_timestamp=int(
            datetime.datetime.utcnow().timestamp()) - 3600 * (shift+1),
        end_timestamp=int(
            datetime.datetime.utcnow().timestamp()) - 3600 * shift,
    )
    return data


if __name__ == "__main__":
    print(json.dumps(main(), indent=4))
