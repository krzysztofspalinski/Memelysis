import json
import os
import urllib.request

from datetime import datetime
from memedroid_scraper import Memedroid


def get_data(start, end):
    """
    Extracts memes information, downloads corresponding images from specified the time interval and creates log.txt
    Arguments:
        -start - timestamp representing the beginning of the interval
        -end - timestamp representing the ending of the interval
    """
    memedroid = Memedroid()
    memedroid.extract_data(start, end)

    date_hour_now = datetime.now().strftime("%Y%m%d%H")
    date_hour_nice = datetime.now().strftime('%Y %m %d, %H:%M')

    log = f'Downloading data from Memedroid on {date_hour_nice}. \n'
    log = log + f'Scanned {memedroid.scanned_memes} memes, found {len(memedroid.data)} memes to download. \n'

    # Save images to folder ./Memedroid
    try:
        os.mkdir('./Memedroid')
    except:
        pass

    meme_number = 1
    for meme in memedroid.data:
        url = meme['url']
        filename = f'memedroid_{date_hour_now}_{meme_number:05}'
        filename = filename + url[-5:]  # File extension

        log = log + f'Downloading {filename} from {url}...'
        try:
            urllib.request.urlretrieve(url, './Memedroid/' + filename)
            meme['filename'] = filename
            log = log + "Done. \n"
        except:
            log = log + "Failed. \n"
        meme_number += 1

    # Save memedroid_date.json file
    json_filename = f'./memedroid_{date_hour_now}.json'

    with open(json_filename, 'w') as f:
        f.write(json.dumps(memedroid.data, indent=1))

    # Save log_date.txt file
    log_filename = f'./memedroid_log_{date_hour_now}.txt'
    with open(log_filename, 'w') as f:
        f.write(log)


if __name__ == '__main__':
    start = datetime.timestamp(datetime.strptime("2020-04-18 20:00:00", '%Y-%m-%d %H:%M:%S'))
    end = datetime.timestamp(datetime.strptime("2020-04-18 23:00:00", '%Y-%m-%d %H:%M:%S'))
    get_data(start, end)
