def get_reddit(start, end):
    import praw
    import urllib
    import json
    from datetime import datetime, timedelta
    start = datetime.timestamp(start)
    end = datetime.timestamp(end)
    
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
        if start <= sub_creation_date < end:
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
        elif start > sub_creation_date:
            break
    
    
    date_hour_now = datetime.now().strftime("%Y%m%d%H")
    date_hour_nice = datetime.now().strftime('%Y %m %d, %H:%M')
    
    log = f'Downloading data from Reddit on {date_hour_nice}. \n' 
    log = log + f'Scanned {scanned_memes} memes, found {len(memes_to_upload)} memes to download. \n'
    
    # Save images to folder ./Reddit
    try:
        os.mkdir('./Reddit')
    except:
        pass
    
    
    meme_number = 1 
    
    for meme in memes_to_upload:
    
        url = meme['url']
        filename = f'reddit_{date_hour_now}_{meme_number:05}'
        filename = filename + url[-4:] # File extension
    
        log = log + f'Downloading {filename} from {url}...'
        try:
            urllib.request.urlretrieve(url, './Reddit/'+filename)
            meme['filename'] = filename
            log = log + "Done. \n"
        except:
            log = log + "Failed. \n"
        meme_number += 1
    
    
    # Save reddit_date.json file
    json_filename = f'./reddit_{date_hour_now}.json'
    
    with open(json_filename, 'w') as f:
        f.write(json.dumps(memes_to_upload, indent=1))
    
    
    #Save log_date.txt file
    log_filename = f'./reddit_log_{date_hour_now}.txt'
    with open(log_filename, 'w') as f:
        f.write(log)
    
    