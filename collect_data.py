from scrappers.datacollector import DataCollector

def main():

    ACCESS_TOKEN = ''
    ACCESS_SECRET = ''
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''

    twitter_credentials = {
        'consumer_key' : CONSUMER_KEY,
        'consumer_secret' : CONSUMER_SECRET,
        'access_token' : ACCESS_TOKEN,
        'access_secret' : ACCESS_SECRET,
        'data_path' : "./scrappers/twitter/mass-storage/"
    }

    datacollector = DataCollector()
    datacollector.connect_to_twitter(twitter_credentials)
    datacollector.collect_data("./test_log.txt",
                               "2020-04-10",
                               "2020-04-11",
                               twitter_tag="meme")

if __name__ == "__main__":
    main()