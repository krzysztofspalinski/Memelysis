def obtain_data_from_reddit(start_timestamp: float, end_timestamp: float, secrets_file_location: str):
    import praw
    from datetime import datetime
    import json

    with open(secrets_file_location) as json_file:
        login_info = json.load(json_file)

    reddit = praw.Reddit(client_id=login_info['client_id'],
                         client_secret=login_info['client_secret'],
                         username=login_info['username'],
                         password=login_info['password'],
                         user_agent=login_info['user_agent'])
    subreddit = reddit.subreddit('memes')
    new_memes = subreddit.new(limit=1500)

    memes_to_download, scanned_memes = get_memes_to_upload(
        new_memes, start_timestamp, end_timestamp)

    date_hour_now = datetime.now().strftime("%Y%m%d%H")
    date_hour_nice = datetime.now().strftime('%Y %m %d, %H:%M')

    log = f'Downloading data from Reddit on {date_hour_nice}. \n'
    log = log + \
        f'Scanned {scanned_memes} memes, found {len(memes_to_download)} memes to download. \n'

    # Save json file
    json_filename = f'./reddit_{date_hour_now}.json'

    with open(json_filename, 'w') as f:
        f.write(json.dumps(memes_to_download, indent=1))

    return memes_to_download


def get_memes_to_upload(new_memes, start_timestamp, end_timestamp):
    import re
    from datetime import datetime
    scanned_memes = 0
    memes_to_upload = []
    date_hour_now = datetime.now().strftime("%Y%m%d%H")

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

            img_url = str(submission.url)
            try:
                img_extension = re.split(
                    r'[^\w]', img_url.split('/')[-1].split('.')[1])[0]
            except:
                img_extension = "png"

            meme = {
                'url': img_url,
                'extension': img_extension,
                'source': "reddit",
                'id': f"{date_hour_now}{scanned_memes:06}",
                'additional_data': data
            }

            memes_to_upload.append(meme)
        elif start_timestamp > sub_creation_date:
            break

    return memes_to_upload, scanned_memes


def main():
    from datetime import datetime
    shift = 3
    data = obtain_data_from_reddit(start_timestamp=datetime.utcnow().timestamp() - 3600 * (shift + 1),
                                   end_timestamp=datetime.utcnow().timestamp() - 3600 * shift,
                                   secrets_file_location='/home/secrets/reddit.json')
    return data


if __name__ == '__main__':
    import json
    print(json.dumps(main()))
