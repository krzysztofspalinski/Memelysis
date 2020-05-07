import os
from twittercollector import TwitterCollector
import unittest

class TwitterCollectorTest(unittest.TestCase):

    def test_1_run_collector(self):
        # credentials
        ACCESS_TOKEN = None
        ACCESS_SECRET = None
        CONSUMER_KEY = None
        CONSUMER_SECRET = None

        DIR = "./test/"
        HASHTAG = "meme"
        self.tc = TwitterCollector(CONSUMER_KEY,
                              CONSUMER_SECRET,
                              ACCESS_TOKEN,
                              ACCESS_SECRET)
        self.tc.save_tweets_with_media(HASHTAG,
                                  start="2020-04-17 23:00:00",
                                  end="2020-04-18 00:00:00",
                                  directory=DIR,
                                  count=100)

    def test_2_files_exist(self):

        directory = "./test/"

        self.assertTrue(os.path.exists(directory))
        self.assertEqual(len(os.listdir(directory)), 3)

    def test_3_proper_filenames(self):

        directory = "./test/"

        for i in os.listdir(directory):
            if '.json' not in i and '.txt' not in i:
                main_name = i
        for i in os.listdir(directory):
            self.assertTrue(main_name in i)

    def test_4_directory_already_exists(self):

        with self.assertRaises(Exception):
            self.tc.save_tweets_with_media("meme", "2020-04-17 23:00:00", "2020-04-18 00:00:00", "./test/")


if __name__ == "__main__":
    unittest.main()
