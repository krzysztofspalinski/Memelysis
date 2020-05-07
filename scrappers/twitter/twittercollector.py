import tweepy
import os
import datetime
from tqdm import tqdm
from urllib.request import urlretrieve
import json

class TwitterCollector:
    """
    Class collects Tweets containing images via Twitter API
    Tweepy doc: http://docs.tweepy.org/en/latest/api.html
    """

    def __init__(self,
                 consumer_key,
                 consumer_secret,
                 access_token,
                 access_secret
                 ):
        """
        Constructor establishes connection to twitter.com
        :param consumer_key:
        :param consumer_secret:
        :param access_token:
        :param access_secret:
        """
        auth = tweepy.OAuthHandler(consumer_key=consumer_key,
                                   consumer_secret=consumer_secret)
        auth.set_access_token(access_token,
                              access_secret)

        self.api = tweepy.API(auth)

        # valid access assertion
        try:
            _ = self.api.home_timeline()
            print("Connection established!")

        except tweepy.TweepError:
            raise Exception("Could not connect Twitter API!")

    def get_user_tweets(self, username):
        return self.api.user_timeline(username)

    def _get_hashtag_tweets(self, hashtag, since, until, count=None):
        """
        Collects tweets by given hashtag and time range
        :param hashtag:
        :param since: start date (format: 'yyyy-mm-dd')
        :param until: end date (format: 'yyyy-mm-dd')
        :param count: 
        :return: tweepy.Cursor object
        """
        # TODO: time range instead of date range

        return tweepy.Cursor(self.api.search,
                             q="#{} since:{} until:{}".format(hashtag, since, until),
                             count=count,
                             lang='en'
                             )

    def save_tweets_with_media(self,
                               hashtag,
                               start,
                               end,
                               directory,
                               count=None):
        """
        Saving tweets from given hashtag containing media to a JSON file
        :param hashtag: collecting tweets with a given tag
        :param start: date format: '%Y-%m-%d %H:%M:%S'
        :param end: date format: '%Y-%m-%d %H:%M:%S'
        :param directory: directory path for output files
        :param count: The number of tweets to return per page
        """

        start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')

        execution_time = datetime.datetime.now()
        # time range tweets are being collected
        since = start.date()
        until = since + datetime.timedelta(days=1)

        tweets = self._get_hashtag_tweets(hashtag, since, until, count)

        # check if directory exists
        if os.path.exists(directory):
            raise Exception("Directory {} already exists!".format(directory))
        else:
            print("Directory {} does not exist! Creating directory...".format(directory))
            os.makedirs(directory)
            storage_dir = directory + "twitter_" + hashtag + "_" + str(int(execution_time.timestamp())) + "/"
            os.makedirs(storage_dir)

        # creating output file
        output_file = directory + "twitter_" + hashtag + "_" + str(int(execution_time.timestamp())) + ".json"
        print("Creating {}...".format(output_file))
        open(output_file, 'a').close()

        # save tweets that contain media files
        print("Saving tweets...")
        TweepErrorReached = False
        meme_counter = 0

        try:
            for tweet in tqdm(tweets.items()):
                    if tweet.entities.get('media', None) is not None and \
                        tweet.created_at >= start and tweet.created_at <= end:
                        # TODO: image/video
                        tweet_json = {"url": tweet.entities['media'][0]['media_url'],
                                      "additional_data": {
                                          "id": tweet.id,
                                          "created_at": str(tweet.created_at),
                                          "text": tweet.text,
                                          "favorite_count": tweet.favorite_count,
                                          "retweet_count": tweet.retweet_count,
                                          "hashtags": tweet.entities['hashtags']}
                                      }

                        try:
                            urlretrieve(tweet_json['url'], storage_dir + str(tweet_json['additional_data']['id']))
                            meme_counter += 1
                        except:
                            print("Cannot download image {}".format(tweet_json['url']))

                        with open(output_file, 'a') as outfile:
                            json.dump(tweet_json, outfile, indent=1)

        except tweepy.TweepError:
            TweepErrorReached = True

        if TweepErrorReached: print("Tweep error reached!")

        # Creating log
        log = {"output_file": output_file,
               "run": str(execution_time),
               "start" : str(start),
               "end" : str(end),
               "linecount" : meme_counter,
               "TweepErrorReached" : TweepErrorReached}

        # check if log file exists
        log_file = directory + "twitter_" + hashtag + "_" + str(int(execution_time.timestamp())) + ".txt"

        if os.path.exists(log_file):
            raise Exception("File {} already exists!".format(log_file))
        else:
            open(log_file, 'a').close()

        # append to log
        with open(log_file, 'a') as outfile:
            json.dump(log, outfile, indent=1)

        return True

    # TODO: API trend methods


def main():

    pass


if __name__ == "__main__":
    main()
