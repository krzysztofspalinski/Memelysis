import json
import os
import sys
import pytz
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil.parser import isoparse
from requests import get


class MemedroidObject:
    """
    Meme from www.memedroid.com website

    Attributes:
        content - html content extracted from www.memedroid.com based on the 'article' tag
        meme_data - a dictionary containing data such as:
                        -title - meme tile
                        -img_url - url of the meme that enables the downloading
                        -tags - a dictionary containing tags attached to the meme (if any)
                        -date - the time at which the meme was uploaded on the website
                        -popularity - the indicator of meme's popularity of the form x%(y), where 'x' stands for the
                                      percentage of likes out of 'y' votes
    """

    def __init__(self, object_content):
        """
        Initialize an object in according to html content extracted from www.memedroid.com based on the 'article' tag
        """
        self.content = object_content
        self.meme_data = {}

    def is_video(self):
        """Check if the meme is a video or an image"""
        if self.content.find('video') is None:
            return False
        else:
            return True

    def add_title(self):
        """Extracts the title of the meme"""
        title = self.content.find('img', {'class': 'img-responsive'})['alt'][:-7]
        self.meme_data['title'] = title

    def add_img_url(self):
        """Extracts the image url of the meme"""
        img_url = self.content.find('img', {'class': 'img-responsive'})['src']
        self.meme_data['img_url'] = img_url

    def add_tags(self):
        """Extracts tags of the meme (if any)"""
        # check if the meme has any tags attached to it
        tags_container = self.content.find('div', {'class': 'tags-container'})
        tags = {}
        if tags_container is None:
            self.meme_data['tags'] = tags
            return
        else:
            all_tags = tags_container.findAll('a', {'class': 'dyn-link'})
            n = len(all_tags)
            for i in range(n):
                tags[f'tag{i + 1}'] = all_tags[i].text
            self.meme_data['tags'] = tags

    def add_date(self):
        """Extracts the uploading time of the meme"""
        date_raw = self.content.time['datetime']
        tz_original = pytz.timezone("America/New_York")
        tz_new = pytz.timezone("Poland")
        date = tz_original.localize(isoparse(date_raw)).astimezone(tz_new)  # changes the timezone from UTC-5 to UTC+1
        date = date.replace(tzinfo=None)  # hides the info about the timezone
        self.meme_data['date'] = str(date)

    def add_popularity(self):
        """Extracts the popularity indicator of the meme"""
        popularity = self.content.find('span', {'class': ['green-1', 'white', 'red-2']}).text + \
                     self.content.find('span', {'class': 'item-rating-vote-count'}).text
        self.meme_data['popularity'] = popularity

    def extract_info(self):
        """
        Checks if it is possible to extract any information based on the html content provided for the meme and extracts
        the data.
        """
        try:
            meme_link = f"https://www.memedroid.com{self.content.find('a', {'class': 'dyn-link'})['href']}"
            try:
                self.add_img_url()
                self.add_title()
                self.add_tags()
                self.add_date()
                self.add_popularity()
            except AttributeError:  # such error indicates that there are some missing values in the data extraction
                with open('memedroid_problems.json', 'w+') as _file:
                    _file.write(json.dumps({'url': meme_link}))
        except AttributeError:
            print('Problems with extracting any data!' + '\n' + self.content)


class Memedroid:
    """
    Memedroid website's content based on the provided url that is associated with the www.memedroid.com website

    Attributes:
        web-url - the url associated with the www.memedroid.com website
        memes - all memes, extracted based on the 'article' tag
        data - a list containing dictionaries with information about memes
    """

    def __init__(self, url):
        """Initialize the object based on the url associated with memedroid"""
        self.web_url = url
        self.memes = []
        self.data = []

    def get_memes(self):
        """Extracts all memes currently displayed."""
        page = get(self.web_url)
        page_soup = BeautifulSoup(page.content, 'html.parser')
        main_section = page_soup.find('div', {'class': 'gallery-memes-container'})
        self.memes = main_section.findAll('article', {'class': 'gallery-item'})

    def extract_memes_info(self):
        """Extracts information about each meme"""
        self.get_memes()
        for i in self.memes:
            meme = MemedroidObject(i)
            if meme.is_video():
                continue
            meme.extract_info()
            self.data.append(meme.meme_data)

    def get_next_page_url(self):
        """
        Returns:
            next_page_url - url of the next website associated with Memedroid
        """
        page = get(self.web_url)
        page_soup = BeautifulSoup(page.content, 'html.parser')
        main_section = page_soup.find('div', {'class': 'gallery-memes-container'})
        next_page_url = f"https://www.memedroid.com{main_section.find('nav', {'class': 'hidden'}).a['href']}"
        return next_page_url

    def extract_data(self, number_of_pages=1):
        """
        Extracts memes' data from current and further websites, which urls are based on the get_next_page_url function

        Arguments:
            -number_of_pages - number of pages from which the data will be extracted
        """
        for i in range(number_of_pages):
            self.extract_memes_info()
            self.content = self.get_next_page_url()


if __name__ == '__main__':
    memedroid = Memedroid('https://www.memedroid.com')
    memedroid.extract_data(10)
    path = os.path.join(sys.path[0],
                        f'memedroid_gallery_images_{datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}.json')

    with open(path, 'w') as file:
        file.write(json.dumps(memedroid.data, indent=4))
