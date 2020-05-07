from twittercredentials import ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET
from twittercollector import TwitterCollector

import datetime

def main():


    tc = TwitterCollector(CONSUMER_KEY,
                          CONSUMER_SECRET,
                          ACCESS_TOKEN,
                          ACCESS_SECRET)

    START = (datetime.datetime.today().now() - datetime.timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
    END = (datetime.datetime.today().now() - datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

    print(tc.save_tweets_with_media("meme",
                              start= START,
                              end = END))


if __name__ == "__main__":
    main()