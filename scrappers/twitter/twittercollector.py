import tweepy
import datetime
import json
import re
import os
import urllib

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

        # result_type: mixed, recent, popular
        return tweepy.Cursor(self.api.search,
                             q="#{} since:{} until:{}".format(hashtag, since, until),
                             count=count,
                             lang='en'
                             )

    def save_tweets_with_media(self,
                               hashtag,
                               start,
                               end,
                               count=None):
        """
        Saving tweets from given hashtag containing media to a JSON file
        :param hashtag: collecting tweets with a given tag
        :param start: date format: '%Y-%m-%d %H:%M:%S'
        :param end: date format: '%Y-%m-%d %H:%M:%S'
        :param count: The number of tweets to return per page
        """

        start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')

        execution_time = datetime.datetime.now()
        # time range tweets are being collected
        since = start.date()
        until = since + datetime.timedelta(days=1)

        tweets = self._get_hashtag_tweets(hashtag, since, until, count)

        # save tweets that contain media files
        twitter_memes = []

        try:

            for tweet in tweets.items():
                if tweet.entities.get('media', None) is not None and \
                    tweet.created_at >= start and tweet.created_at <= end:

                    image_url = tweet.entities['media'][0]['media_url']

                    try:
                        _, ext = os.path.splitext(image_url)
                        image_extension = ext[1:]
                    except KeyError:
                        image_extension = "png"

                    tweet_dict = {"url": image_url,
                                  "extension":image_extension,
                                  "id": tweet.id,
                                  "source": "twitter",
                                  "additional_data": {
                                      "created_at": str(tweet.created_at),
                                      "text": tweet.text,
                                      "favorite_count": tweet.favorite_count,
                                      "retweet_count": tweet.retweet_count,
                                      "hashtags": tweet.entities['hashtags']}
                                  }

                    twitter_memes.append(tweet_dict)
        except tweepy.TweepError:
            pass

        return json.dumps(twitter_memes, indent=4)

def main():

    pass


if __name__ == "__main__":
    main()
