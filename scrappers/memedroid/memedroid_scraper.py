import json
import pytz
import requests

from datetime import datetime
from bs4 import BeautifulSoup
from dateutil.parser import isoparse


class MemedroidObject:
    """
    Meme from www.memedroid.com website

    Attributes:
        content - html content extracted from www.memedroid.com based on the 'article' tag
        url - meme url
        meme_data - a dictionary containing data such as:
                        -title - meme tile
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
        self.url = ''
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
        self.url = img_url

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
                tags[f'tag{i + 1}'] = all_tags[i].text.strip()
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
        popularity = self.content.find('span', {'class': ['green-1', 'white', 'red-2']}).text.strip() + \
                     self.content.find('span', {'class': 'item-rating-vote-count'}).text.strip()
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
            except TypeError:  # such error indicates that there are some missing values in the data extraction
                with open('memedroid_problems.json', 'w+') as _file:
                    _file.write(json.dumps({f'url{datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}': meme_link}))
        except TypeError:
            print('Problems with extracting any data!' + '\n' + self.content)


class Memedroid:
    """
    Memedroid website's content based on the provided url that is associated with the www.memedroid.com website

    Attributes:
        web-url - the url associated with the www.memedroid.com website
        memes - a list with dictionaries that represent all memes, extracted based on the 'article' tag
        data - a list containing dictionaries with information about memes
        scanned_memes - number of scanned memes
    """

    def __init__(self, url='https://www.memedroid.com'):
        """Initialize the object based on the url associated with memedroid"""
        self.web_url = url
        self.memes = []
        self.data = []
        self.scanned_memes = 0

    def get_memes(self, test_time=False):
        """
        Extracts all memes currently displayed. For unit test purposes, test_time argument was added as to check
        the access to the website.
        """
        page = requests.get(self.web_url)
        if test_time:
            return
        page_soup = BeautifulSoup(page.content, 'html.parser')
        main_section = page_soup.find('div', {'class': 'gallery-memes-container'})
        self.memes = main_section.findAll('article', {'class': 'gallery-item'})

    def extract_data(self, start, end):
        """Extracts information about each meme in self.memes in defined a time interval start:end
        Arguments:
            -start - datetime object that represent the begging of the interval
            -end - datetime object that represent the ending of the interval
        """
        try:
            start = datetime.timestamp(start)
            end = datetime.timestamp(end)
        except TypeError:
            print('Wrong data format')
            return

        # search for data that correspond to given interval
        carry_on = True
        while carry_on:
            self.get_memes()
            for i in self.memes:
                self.scanned_memes += 1
                meme = MemedroidObject(i)
                if meme.is_video():
                    continue
                meme.extract_info()
                tmp_date = datetime.timestamp(datetime.strptime(meme.meme_data['date'], '%Y-%m-%d %H:%M:%S'))
                # current meme is too new
                if end < tmp_date:
                    continue
                # current meme is in the given interval
                elif start <= tmp_date <= end:
                    self.data.append({'url': meme.url,
                                      'additional_data': meme.meme_data})
                # current meme is too old
                else:
                    carry_on = False
            # memes can be on the next page if current page doesnt correspond to given interval
            self.web_url = self.get_next_page_url()

    def get_next_page_url(self):
        """
        Returns:
            next_page_url - url of the next website associated with Memedroid
        """
        page = requests.get(self.web_url)
        page_soup = BeautifulSoup(page.content, 'html.parser')
        main_section = page_soup.find('div', {'class': 'gallery-memes-container'})
        next_page_url = f"https://www.memedroid.com{main_section.find('nav', {'class': 'hidden'}).a['href']}"
        return next_page_url
