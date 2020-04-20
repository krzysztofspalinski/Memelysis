import os
from twittercollector import TwitterCollector

def test_files_exist(directory):

    # check if directory and output files have been properly created
    assert os.path.exists(directory)
    assert len(os.listdir(directory)) == 3

    for i in os.listdir(directory):
        if '.json' not in i and '.txt' not in i:
            main_name = i
    for i in os.listdir(directory):
        assert main_name in i


    return "Test passed!"

def test_directory_already_exists(tc,
                                  hashtag,
                                  start,
                                  end,
                                  dir):
    #check if TwitterCollector starts if directory already exists

    try:
        tc.save_tweets_with_media(hashtag, start, end, dir)
    except Exception:
        return "Test passed!"

def main():
    #example use
    ACCESS_TOKEN = None
    ACCESS_SECRET = None
    CONSUMER_KEY = None
    CONSUMER_SECRET = None
    DIR = "./test/"
    HASHTAG = "meme"
    tc = TwitterCollector(CONSUMER_KEY,
                          CONSUMER_SECRET,
                          ACCESS_TOKEN,
                          ACCESS_SECRET)
    tc.save_tweets_with_media(HASHTAG,
                              start="2020-04-17 23:00:00",
                              end="2020-04-18 00:00:00",
                              directory=DIR)

    print(test_files_exist(DIR))
    print(test_directory_already_exists(tc, HASHTAG, "2020-04-17 23:00:00", "2020-04-18 00:00:00", DIR))



if __name__ == "__main__":
    main()