import tweepy
import os
import datetime
from tqdm import tqdm

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
                               since,
                               until,
                               data_path,
                               count=None):
        """
        Saving tweets from given hashtag containing media to a JSON file
        :param hashtag:
        :param since:
        :param until:
        :param data_path:
        :param count:
        :return:
        """

        tweets = self._get_hashtag_tweets(hashtag, since, until, count)

        # check if data_path exists
        if os.path.exists(data_path):
            print("Directory {} already exists!".format(data_path))
        else:
            print("Directory {} does not exist! Creating directory...".format(data_path))
            os.makedirs(data_path)

        # creating output file
        output_file = data_path + hashtag + "_" + since + "_" + until + "_" + str(
            datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")) + ".json"
        print("Creating {}...".format(output_file))
        open(output_file, 'a').close()

        # save tweets that contain media files
        # TODO: check if we deal with image/video
        print("Saving tweets...")
        for tweet in tqdm(tweets.items()):
            #TODO: catch tweepy.TweepError
            if tweet.entities.get('media', None) is not None:
                tweet_json = {"id": tweet.id,
                              "text": tweet.text,
                              "favorite_count": tweet.favorite_count,
                              "hashtags": tweet.entities['hashtags'],
                              "media": tweet.entities['media']}
                with open(output_file, 'a') as file:
                    file.write(str(tweet_json) + "\n")

        print("Done!")
        return output_file

    # TODO: API trend methods


def main():

    pass


if __name__ == "__main__":
    main()
