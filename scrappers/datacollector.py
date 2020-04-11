from scrappers.twitter.twittercollector import  TwitterCollector
import os

class DataCollector:

    def __init__(self):
        pass

    def connect_to_twitter(self,
                           twitter_credentials):
        self.twitter = TwitterCollector(
            twitter_credentials['consumer_key'],
            twitter_credentials['consumer_secret'],
            twitter_credentials['access_token'],
            twitter_credentials['access_secret']
        )
        self._twitter_data_path = twitter_credentials['data_path']

    # TODO:
    def connect_to_reddit(self):
        pass

    def collect_data(self,
                     log_file,
                     start,
                     end,
                     twitter_tag):
        """

        :return:
        """

        # check if log file exists
        if os.path.exists(log_file):
            print("File {} already exists!".format(log_file))
        else:
            open(log_file, 'a').close()

        log = {}

        # Twitter log
        twitter_output = self.twitter.save_tweets_with_media(twitter_tag,
                                                             start,
                                                             end,
                                                             self._twitter_data_path)

        log['twitter'] = {"output_file": twitter_output,
                          "start" : start,
                          "end" : end,
                          "linecount" : sum(1 for line in open(twitter_output))}

        #TODO: reddit log
        #TODO: memedroid log

        # append to log
        with open(log_file, 'a') as file:
            file.write(str(log) + "\n")

        return

def main ():
    pass



if __name__ == "__main__":
    main()

    from scrappers.twitter.twittercollector import TwitterCollector


    def main():
        ACCESS_TOKEN = '1239665309491048453-3eHz4SiYPMCEL2lVVVDCTz8LDA9JmF'
        ACCESS_SECRET = 'aCCAkQ9twiQTLwGVDqb0POzUIM5ODKEWv2vfE6yuqbKlF'
        CONSUMER_KEY = 'BpCtjXyHE3lvmgHWbbTZzbvtx'
        CONSUMER_SECRET = '22vKmW2QRLeEgxbBvUHVFAusPu8aQi3JUaUbirkjllAGzmvWIS'

        tc = TwitterCollector(CONSUMER_KEY,
                              CONSUMER_SECRET,
                              ACCESS_TOKEN,
                              ACCESS_SECRET)
        tc.save_tweets_with_media("bigdata",
                                  "2020-03-28",
                                  "2020-03-29",
                                  "./scrappers/twitter/mass-storage/")


    if __name__ == "__main__":
        main()