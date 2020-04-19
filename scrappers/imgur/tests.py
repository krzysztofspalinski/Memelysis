from datetime import datetime
from unittest import TestCase, main
import random
import os
import sys
import imgur_scraper


class ImgurScrapperTests(TestCase):

    def test_obtain_data_from_imgur_returns_data_in_correct_timestamp_window(self):
        start_timestamp = int(datetime.utcnow().timestamp()) - random.randint(3600, 3600*6)
        end_timestamp = int(datetime.utcnow().timestamp())
        data = imgur_scraper.obtain_data_from_imgur(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp
        )
        min_timestamp = min(data, key=lambda x: x["datetime"])["datetime"]
        max_timestamp = max(data, key=lambda x: x["datetime"])["datetime"]
        self.assertIn(min_timestamp, range(start_timestamp, end_timestamp))
        self.assertIn(max_timestamp, range(start_timestamp, end_timestamp))

    def test_obtain_data_from_imgur_creates_json(self):
        start_timestamp = int(datetime.utcnow().timestamp()) - random.randint(3600, 3600*2)
        end_timestamp = int(datetime.utcnow().timestamp())
        imgur_scraper.obtain_data_from_imgur(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp
        )
        self.assertTrue(len([x for x in os.listdir(sys.path[0]) if x.startswith("imgur") and x.endswith(".json")]) > 0)

    def test_obtain_data_from_imgur_creates_log(self):
        start_timestamp = int(datetime.utcnow().timestamp()) - random.randint(3600, 3600*2)
        end_timestamp = int(datetime.utcnow().timestamp())
        imgur_scraper.obtain_data_from_imgur(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp
        )
        self.assertTrue(len([x for x in os.listdir(sys.path[0]) if x.startswith("imgur") and x.endswith(".txt")]) > 0)


if __name__ == '__main__':
    main()
