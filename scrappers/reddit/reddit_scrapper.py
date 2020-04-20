def download_images(memes_to_download: list, log: str, date_hour_now: str, file_location='./Reddit'):
    import urllib.request
    import os

    try:
        os.mkdir(file_location)
    except FileExistsError:
        pass
    finally:
        pass
    meme_number = 1

    for meme in memes_to_download:

        url = meme['url']
        filename = f'reddit_{date_hour_now}_{meme_number:05}'
        filename = filename + url[-4:]  # File extension

        log = log + f'Downloading {filename} from {url}... '
        try:
            urllib.request.urlretrieve(url, './Reddit/' + filename)
            meme['filename'] = filename
            log = log + "Done. \n"
        except ValueError:
            log = log + "Failed, unknown url. \n"
        finally:
            pass

        meme_number += 1
    return memes_to_download, log


def get_memes_to_upload(new_memes, start_timestamp, end_timestamp):
    scanned_memes = 0
    memes_to_upload = []

    for submission in new_memes:
        sub_creation_date = submission.created_utc
        scanned_memes += 1
        if start_timestamp <= sub_creation_date < end_timestamp:
            data = {
                'date': sub_creation_date,
                'title': str(submission.title),
                'upvotes': int(submission.score),
                'upvote_ratio': float(submission.upvote_ratio)
            }

            meme = {
                'url': str(submission.url),
                'additional_data': data
            }

            memes_to_upload.append(meme)
        elif start_timestamp > sub_creation_date:
            break

    return memes_to_upload, scanned_memes


def reddit_scraper(start_timestamp: float, end_timestamp: float, secrets_file_location: str):
    import praw
    import json
    from datetime import datetime

    with open(secrets_file_location) as json_file:
        login_info = json.load(json_file)

    reddit = praw.Reddit(client_id=login_info['client_id'],
                         client_secret=login_info['client_secret'],
                         username=login_info['username'],
                         password=login_info['password'],
                         user_agent=login_info['user_agent'])
    subreddit = reddit.subreddit('memes')
    new_memes = subreddit.new(limit=1500)

    memes_to_download, scanned_memes = get_memes_to_upload(new_memes, start_timestamp, end_timestamp)

    date_hour_now = datetime.now().strftime("%Y%m%d%H")
    date_hour_nice = datetime.now().strftime('%Y %m %d, %H:%M')

    log = f'Downloading data from Reddit on {date_hour_nice}. \n'
    log = log + f'Scanned {scanned_memes} memes, found {len(memes_to_download)} memes to download. \n'

    # Download images to folder ./Reddit
    memes_to_download, log = download_images(memes_to_download, log, date_hour_now)

    # Save json file
    json_filename = f'./reddit_{date_hour_now}.json'

    with open(json_filename, 'w') as f:
        f.write(json.dumps(memes_to_download, indent=1))

    # Save log file
    log_filename = f'./reddit_log_{date_hour_now}.txt'
    with open(log_filename, 'w') as f:
        f.write(log)
