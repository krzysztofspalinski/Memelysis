import unittest
from reddit_scrapper import download_images, get_memes_to_upload, reddit_scraper


class TestEmployee(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_download(self):
        try:
            mocked_memes_list = [{'url': 'NotAValidURL',
                                  'source': 'Reddit'}]
            download_images(mocked_memes_list, '', '')
        except ValueError:
            self.fail("Function crashed unexpectedly!")

    def test_file_creation(self):
        from datetime import datetime, timedelta
        import os
        time_now = datetime.now()
        time_start = datetime.timestamp(time_now - timedelta(minutes=5))
        time_end = datetime.timestamp(time_now)

        date_hour_now = datetime.now().strftime("%Y%m%d%H")
        json_filename = f'./reddit_{date_hour_now}.json'
        log_filename = f'./reddit_log_{date_hour_now}.txt'

        reddit_scraper(time_start, time_end, '../../secrets/reddit.json')

        self.assertTrue(os.path.exists(json_filename))
        self.assertTrue(os.path.exists(log_filename))


if __name__ == '__main__':
    unittest.main()