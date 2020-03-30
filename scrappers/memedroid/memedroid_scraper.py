import os
import pytz

from csv import writer
from bs4 import BeautifulSoup
from dateutil.parser import isoparse
from requests import get


def get_url(object_meme):
    return object_meme.find('img', {'class': 'img-responsive'})['src']


def extract_data(object_meme):
    url = get_url(object_meme)
    title = object_meme.find('img', {'class': 'img-responsive'})['alt']
    tags_raw = object_meme.findAll('a', {'data-title-container': '#tags-gallery-section'})
    if len(tags_raw) > 0:
        tags = [i.text for i in tags_raw]
    else:
        tags = []
    date_raw = object_meme.time['datetime']
    tz_original = pytz.timezone("America/New_York")
    tz_new = pytz.timezone("Poland")
    date = tz_original.localize(isoparse(date_raw)).astimezone(tz_new)
    date = date.replace(tzinfo=None)
    popularity = object_meme.find('span', {'class': ['green-1', 'white', 'red-2']}).text + \
                 object_meme.find('span', {'class': 'item-rating-vote-count'}).text
    return [title, url, tags, date, popularity]


def main():
    page = get('https://www.memedroid.com')
    page_soup = BeautifulSoup(page.content, 'html.parser')
    main_section = page_soup.find('section', {'class': 'default-section'})
    all_memes = main_section.findAll('article')
    for i in all_memes:
        try:
            list_of_elem = extract_data(i)

            if 'links.csv' in os.listdir():
                with open('links.csv', 'a+', newline='') as write_obj:
                    csv_writer = writer(write_obj)
                    csv_writer.writerow(list_of_elem)
            else:
                with open('links.csv', 'w') as write_obj:
                    csv_writer = writer(write_obj)
                    csv_writer.writerow(['title', 'url', 'tags', 'date', 'popularity'])
                    csv_writer.writerow(list_of_elem)
        except:
            url = [get_url(i)]
            if 'links_with_problems.csv' in os.listdir():
                with open('links.csv', 'a+', newline='') as write_obj:
                    csv_writer = writer(write_obj)
                    csv_writer.writerow(url)
            else:
                with open('links_with_problems.csv', 'w') as write_obj:
                    csv_writer = writer(write_obj)
                    csv_writer.writerow()
                    csv_writer.writerow(url)


if __name__ == "__main__":
    main()
