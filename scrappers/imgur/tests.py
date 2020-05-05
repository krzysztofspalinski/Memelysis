from datetime import datetime
from unittest import TestCase, main
import os
import sys
import shutil
import imgur_scraper


class ImgurScrapperTests(TestCase):
    def setUp(self):
        start_timestamp = int(datetime.utcnow().timestamp()) - 3600 * 2
        end_timestamp = int(datetime.utcnow().timestamp())
        images = imgur_scraper.obtain_data_from_imgur(
            page=-1,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            temporary=True
        )
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.images = images

    def tearDown(self):
        tmp_path = os.path.join(sys.path[0], "tmp")
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path, ignore_errors=True)

    def test_obtain_data_from_imgur_returns_data_in_correct_timestamp_window(self):
        if len(self.images) > 0:
            min_timestamp = min(self.images, key=lambda x: x.get(
                "additional_data", {}).get("date")).get("additional_data", {}).get("date")
            max_timestamp = max(self.images, key=lambda x: x.get(
                "additional_data", {}).get("date")).get("additional_data", {}).get("date")
            self.assertIn(min_timestamp, range(
                self.start_timestamp, self.end_timestamp))
            self.assertIn(max_timestamp, range(
                self.start_timestamp, self.end_timestamp))

    def test_obtain_data_from_imgur_downloads_images(self):
        self.assertTrue(os.path.exists(
            os.path.join(sys.path[0], "tmp", "imgur")))
        if len(self.images) > 0:
            self.assertTrue(
                len(os.listdir(os.path.join(sys.path[0], "tmp", "imgur"))) > 0)

    def test_obtain_data_from_imgur_creates_json_file(self):
        self.assertTrue(len([x for x in os.listdir(os.path.join(
            sys.path[0], "tmp")) if x.startswith("imgur") and x.endswith(".json")]) > 0)

    def test_obtain_data_from_imgur_creates_log(self):
        self.assertTrue(len([x for x in os.listdir(os.path.join(
            sys.path[0], "tmp")) if x.startswith("imgur") and x.endswith(".txt")]) > 0)

    def test_obtain_data_from_imgur_returns_data_in_correct_format(self):
        for image in self.images:
            self.assertIn("url", image.keys())
            self.assertIn("additional_data", image.keys())
            self.assertIn("date", image.get('additional_data', {}).keys())
            self.assertIn("title", image.get('additional_data', {}).keys())


if __name__ == '__main__':
    main()
