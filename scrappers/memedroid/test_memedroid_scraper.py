import unittest

from datetime import datetime
from unittest.mock import patch
from bs4 import BeautifulSoup
from memedroid_scraper import MemedroidObject, Memedroid


class TestMemedroidObject(unittest.TestCase):

    def setUp(self):
        with open('meme_obj1.html', 'r') as f:
            webpage = f.read()
            self.meme_obj1 = MemedroidObject(BeautifulSoup(webpage, 'html.parser'))
        with open('meme_obj2.html', 'r') as f:
            webpage = f.read()
            self.meme_obj2 = MemedroidObject(BeautifulSoup(webpage, 'html.parser'))
        self.not_a_meme = MemedroidObject('')

    def tearDown(self):
        pass

    def test_is_video(self):
        self.assertEqual(self.meme_obj1.is_video(), False)
        self.assertEqual(self.meme_obj2.is_video(), True)

    def test_add_title(self):
        self.meme_obj1.add_title()
        self.assertEqual(self.meme_obj1.meme_data['title'], "Follow me for a follow back")

    def test_add_img_url(self):
        self.meme_obj1.add_img_url()
        self.assertEqual(self.meme_obj1.url,
                         "https://images7.memedroid.com/images/UPLOADED846/5e8fdd868a1f9.jpeg")

    def test_add_tags(self):
        self.meme_obj1.add_tags()
        self.assertEqual(self.meme_obj1.meme_data['tags'], {'tag1': 'loading artist',
                                                            'tag2': 'memes'})
        self.meme_obj2.add_tags()
        self.assertEqual(self.meme_obj2.meme_data['tags'], {'tag1': 'Meme',
                                                            'tag2': 'Face',
                                                            'tag3': 'original',
                                                            'tag4': 'cool',
                                                            'tag5': 'rage',
                                                            'tag6': 'comic',
                                                            'tag7': 'funny',
                                                            'tag8': 'gif',
                                                            'tag9': 'awesome',
                                                            'tag10': 'video',
                                                            'tag11': 'superilluminati',
                                                            'tag12': 'Creator'})

    def test_add_date(self):
        self.meme_obj1.add_date()
        self.assertEqual(self.meme_obj1.meme_data['date'], '2020-04-10 18:01:06')
        self.meme_obj2.add_date()
        self.assertEqual(self.meme_obj2.meme_data['date'], '2017-10-19 21:00:15')

    def test_add_popularity(self):
        self.meme_obj1.add_popularity()
        self.assertEqual(self.meme_obj1.meme_data['popularity'], '56%(117)')
        self.meme_obj2.add_popularity()
        self.assertEqual(self.meme_obj2.meme_data['popularity'], '72%(1246)')

    def test_extract_info(self):
        self.assertRaises(TypeError, self.meme_obj2.extract_info())
        self.assertRaises(TypeError, self.not_a_meme.extract_info())


class TestMemedroid(unittest.TestCase):
    def setUp(self):
        self.obj1 = Memedroid()
        self.obj2 = Memedroid('https://www.memedroid.com/memes/latest/1587240095')

    def tearDown(self):
        pass

    def test_get_memes(self):
        with patch('memedroid_scraper.requests.get') as mocked_get:
            self.obj1.get_memes(test_time=True)
            mocked_get.assert_called_with('https://www.memedroid.com')
        self.setUp()
        self.obj1.get_memes()
        self.assertNotEqual(len(self.obj1.memes), 0)

    def test_extract_data(self):
        start = datetime.strptime('2020-04-18 00:00:00', '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime('2020-04-19 00:00:00', '%Y-%m-%d %H:%M:%S')
        self.assertRaises(TypeError, self.obj1.extract_data('2020', end))
        self.obj1.extract_data(start, end)
        self.assertEqual(len(self.obj1.data), 163)
        url_list = [i['url'] for i in self.obj1.data]
        self.assertIn("https://images3.memedroid.com/images/UPLOADED799/5e9a23d79e423.jpeg", url_list)
        self.assertIn('https://images7.memedroid.com/images/UPLOADED782/5e9a0dfc3127a.jpeg', url_list)
        self.assertIn('https://images7.memedroid.com/images/UPLOADED582/5e99dd9290df4.jpeg', url_list)

    def test_get_next_page_url(self):
        page_url = self.obj2.get_next_page_url()
        self.assertEqual('https://www.memedroid.com/memes/latest/1587240020', page_url)


if __name__ == '__main__':
    unittest.main()
