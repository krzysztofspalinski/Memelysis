import json
import datetime
import sys
import os
import urllib
import requests
from credentials import AUTHORIZATION


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

    date_hour_now = datetime.datetime.now().strftime("%Y%m%d%H")
    date_hour_nice = datetime.datetime.utcnow().strftime('%Y %m %d, %H:%M')

    if temporary is True:
        container_path = os.path.join(sys.path[0], "tmp")
    else:
        container_path = os.path.join(sys.path[0])

    # Obtain post list

    log.append(f"Downloading data from imgur on {date_hour_nice}.")

    if int(page) != -1:
        attempts = 0
        while attempts < max_attempts:
            try:
                url = f'https://api.imgur.com/3/g/memes/{sort}/{window}/{page}'
                response = requests.get(url, headers=headers)
                posts = [post for post in response.json().get('data', []) if start_timestamp <= post["datetime"] < end_timestamp]
                break
            except requests.exceptions.ConnectionError:
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
                    more_posts = [post for post in response.json().get('data', []) if start_timestamp <= post["datetime"] < end_timestamp]
                    posts.extend(more_posts)
                    break
                except requests.exceptions.ConnectionError:
                    attempts += 1
            if len(more_posts) < 60:
                break

    posts = [post for post in posts if all("image" in image.get("type", '') for image in post.get('images', []))]
    log.append(f'Found {len(posts)} memes to download.')

    # Save images in imgur dictionary

    imgur_dir = os.path.join(container_path, "imgur")

    if not os.path.exists(imgur_dir):
        os.makedirs(imgur_dir)

    images = []

    for post in posts:

        post_date = post.get("datetime")
        post_title = post.get("title")
        post_additional_data = {
            "date": post_date,
            "title": post_title
        }
        post_additional_data.update({k: v for k, v in post.items() if k not in ["datetime", "title"]})
        for image in post.get("images", []):

            post_timestamp = post_date
            image_id = image["id"]
            image_url = image["link"]

            try:
                file_extension = image_url.split('/')[-1].split('.')[1]
            except KeyError:
                file_extension = "png"

            file_name = f"imgur_{post_timestamp}_{image_id}.{file_extension}"

            image_path = os.path.join(imgur_dir, file_name)

            log.append(f'Downloading {image_path} from {image_url}.')
            try:
                urllib.request.urlretrieve(image_url, image_path)
                log.append(f'Done.')
            except ValueError:
                log.append("Failed, unknown url")
            except:
                log.append("Failed.")

            images.append({
                'url': image_url,
                'additional_data': post_additional_data,
            })

    # Save json file

    json_path = os.path.join(container_path, f'imgur_{date_hour_now}.json')
    with open(json_path, 'w') as file_:
        file_.write(json.dumps(images, indent=1))

    # Save log file

    log_path = os.path.join(container_path, f'imgur_{date_hour_now}.txt')
    log = "\n".join(log)
    with open(log_path, 'w') as file_:
        file_.write(log)

    return images


def main():
    """Obtains images from imgur.com
    """

    obtain_data_from_imgur(
        page=-1,
        window="day"
    )


if __name__ == "__main__":
    main()
