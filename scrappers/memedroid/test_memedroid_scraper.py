import unittest
from bs4 import BeautifulSoup
from memedroid_scraper import MemedroidObject


class TestMemedroidObject(unittest.TestCase):

    def setUp(self):
        with open('meme_obj1.html', 'r') as f:
            webpage = f.read()
            self.meme_obj1 = MemedroidObject(BeautifulSoup(webpage, 'html.parser'))

    def tearDown(self):
        pass

    def test_is_video(self):
        self.assertEqual(self.meme_obj1.is_video(), False)

    def test_add_title(self):
        self.meme_obj1.add_title()
        self.assertEqual(self.meme_obj1.meme_data['title'], "Follow me for a follow back")

    def test_add_img_url(self):
        self.meme_obj1.add_img_url()
        self.assertEqual(self.meme_obj1.meme_data['img_url'],
                         "https://images7.memedroid.com/images/UPLOADED846/5e8fdd868a1f9.jpeg")

    def test_add_tags(self):
        self.meme_obj1.add_tags()
        self.assertEqual(self.meme_obj1.meme_data['tags'], {'tag1': 'loading artist',
                                                            'tag2': 'memes'})

    def test_add_date(self):
        self.meme_obj1.add_date()
        self.assertEqual(self.meme_obj1.meme_data['date'], '2020-04-10 18:01:06')

    def test_add_popularity(self):
        self.meme_obj1.add_popularity()
        self.assertEqual(self.meme_obj1.meme_data['popularity'], '56%(117)')


if __name__ == '__main__':
    unittest.main()
