import json
import datetime
import sys
import os
import requests


def return_imgur_gallery_images(section="hot", sort="time", page=0, window="day", show_viral="true"):
    """Obtains images from imgur.com

    Args:
        section (str, optional): hot | top | user. Defaults to "hot".
        sort (str, optional): viral | top | time | rising (only available with user section). Defaults to "time".
        page (int, optional): The data paging number. If is equal to -1, then it returns all available images. Defaults to 0.
        window (str, optional): Change the date range of the request if the section is "top", day | week | month | year | all. Defaults to "day".
        showViral (str, optional): true | false - Show or hide viral images from the 'user' section. Defaults to "true".

    Returns:
        dict: Images in the gallery.
    """

    headers = {
        'Authorization': 'Client-ID 20defc4dd62017a',
    }

    max_attempts = 3
    images = []

    if int(page) != -1:
        attempts = 0
        while attempts < max_attempts:
            try:
                url = f'https://api.imgur.com/3/gallery/{section}/{sort}/{window}/{page}?showViral={show_viral}'
                response = requests.get(url, headers=headers)
                images = response.json().get('data', [])
                print(f"Processed {url}")
                break
            except requests.exceptions.ConnectionError:
                attempts += 1
    else:
        while True:
            page += 1
            attempts = 0
            more_images = []
            while attempts < max_attempts:
                try:
                    url = f'https://api.imgur.com/3/gallery/{section}/{sort}/{window}/{page}?showViral={show_viral}'
                    response = requests.get(url, headers=headers)
                    more_images = response.json().get('data', [])
                    images.append(more_images)
                    print(f"Processed {url}")
                    break
                except requests.exceptions.ConnectionError:
                    attempts += 1
            if len(more_images) < 60:
                break
    return images


def main():
    """Obtains images from imgur.com
    """

    imgur_gallery_images = return_imgur_gallery_images(
        page=-1,
        window="day"
    )
    path = os.path.join(sys.path[0], f'imgur_gallery_images_{datetime.datetime.utcnow().strftime("%Y-%m-%d_%H_%M_%S")}.json')
    with open(path, 'w') as file_:
        file_.write(json.dumps(imgur_gallery_images, indent=4))


if __name__ == "__main__":
    main()
