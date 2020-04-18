def download_memes_from_reddit(start_timestamp, end_timestamp, secrets_file_location):
    import praw
    import urllib
    import json
    import os
    from datetime import datetime
    start_timestamp = datetime.timestamp(start_timestamp)
    end_timestamp = datetime.timestamp(end_timestamp)

    with open(secrets_file_location) as json_file:
        login_info = json.load(json_file)

    reddit = praw.Reddit(client_id=login_info['client_id'],
                         client_secret=login_info['client_secret'],
                         username=login_info['username'],
                         password=login_info['password'],
                         user_agent=login_info['user_agent'])
    subreddit = reddit.subreddit('memes')
    new_memes = subreddit.new(limit=1500)

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

    date_hour_now = datetime.now().strftime("%Y%m%d%H")
    date_hour_nice = datetime.now().strftime('%Y %m %d, %H:%M')

    log = f'Downloading data from Reddit on {date_hour_nice}. \n'
    log = log + f'Scanned {scanned_memes} memes, found {len(memes_to_upload)} memes to download. \n'

    # Save images to folder ./Reddit
    try:
        os.mkdir('./Reddit')
    except FileExistsError:
        pass
    finally:
        pass
    meme_number = 1

    for meme in memes_to_upload:

        url = meme['url']
        filename = f'reddit_{date_hour_now}_{meme_number:05}'
        filename = filename + url[-4:]  # File extension

        log = log + f'Downloading {filename} from {url}...'
        try:
            urllib.request.urlretrieve(url, './Reddit/' + filename)
            meme['filename'] = filename
            log = log + "Done. \n"
        except ValueError:
            log = log + "Failed, unknown url. \n"
        finally:
            log = log + "Failed \n"

        meme_number += 1

    # Save json file
    json_filename = f'./reddit_{date_hour_now}.json'

    with open(json_filename, 'w') as f:
        f.write(json.dumps(memes_to_upload, indent=1))

    # Save log file
    log_filename = f'./reddit_log_{date_hour_now}.txt'
    with open(log_filename, 'w') as f:
        f.write(log)
