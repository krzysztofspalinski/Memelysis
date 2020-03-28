import tweepy

class TwitterCollector
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

    def get_hashtag_tweets(self, hashtag, count, since):
        return tweepy.Cursor(self.api.search,
                             q=f"#{hashtag}",
                             count=count,
                             since=since,
                             lang='en'
                             )

    #TODO: API trend methods

def main():
    pass

if __name__ == "__main__":
    main()