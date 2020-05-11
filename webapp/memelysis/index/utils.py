from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import time
import numpy as np
import base64
import urllib.request
from io import BytesIO
import matplotlib

matplotlib.use('Agg')


def get_distribution_plot(meme_score: int, meme_source: str):

    if meme_source == 'reddit':
        try:
            data = np.fromfile('reddit_upvote', dtype=np.int32)
        except:
            url = 'https://storage.googleapis.com/images-and-logs/distributions/reddit_upvote'
            urllib.request.urlretrieve(url, './reddit_upvote')
            data = np.fromfile('reddit_upvote', dtype=np.int32)
        hist, bins, _ = plt.hist(data, bins=50)
        bins = np.logspace(np.log10(bins[0]), np.log10(bins[-1]), len(bins))
        plt.close('all')
        plt.xscale('log')

    if meme_source == 'twitter':
        try:
            data = np.fromfile('twitter_upvote', dtype=np.int32)
        except:
            url = 'https://storage.googleapis.com/images-and-logs/distributions/twitter_upvote'
            urllib.request.urlretrieve(url, './twitter_upvote')
            data = np.fromfile('twitter_upvote', dtype=np.int32)
        hist, bins, _ = plt.hist(data, bins=10)
        bins = np.logspace(np.log10(bins[0]), np.log10(bins[-1]), len(bins))
        plt.close('all')
        plt.xscale('log')

    if meme_source == 'memedroid':
        try:
            data = np.fromfile('memedroid_upvote', dtype=np.int32)
        except:
            url = 'https://storage.googleapis.com/images-and-logs/distributions/memedroid_upvote'
            urllib.request.urlretrieve(url, './memedroid_upvote')
            data = np.fromfile('memedroid_upvote', dtype=np.int32)
        hist, bins, _ = plt.hist(data, bins=25)
        plt.close('all')

    if meme_source == 'imgur':
        try:
            data = np.fromfile('imgur_upvote', dtype=np.int32)
        except:
            url = 'https://storage.googleapis.com/images-and-logs/distributions/imgur_upvote'
            urllib.request.urlretrieve(url, './imgur_upvote')
            data = np.fromfile('imgur_upvote', dtype=np.int32)
        hist, bins, _ = plt.hist(data, bins=20)
        bins = np.logspace(np.log10(bins[0]), np.log10(bins[-1]), len(bins))
        plt.close('all')
        plt.xscale('log')

    fig = plt.gcf()
    fig.set_size_inches(12, 6)

    hist, _, _ = plt.hist(data, bins=bins)

    image = BytesIO()

    plt.ylabel('Number of memes in bin', fontsize=18)
    plt.xlabel('Number of upvotes', fontsize=18)

    plt.ylim(0, max(hist)*1.05)

    plt.vlines(meme_score, 0, max(hist)*1.05, colors='red', lw=5)

    blue_label = 'Distribution of ' + str(meme_source) + ' scores'

    red_patch = mpatches.Patch(color='red', label=r'This meme score')
    blue_patch = mpatches.Patch(color='blue', label=blue_label)

    plt.legend(handles=[red_patch, blue_patch],
               loc='best', fontsize=14, framealpha=0.95)

    plt.savefig(image, format='png')
    image.seek(0)
    return base64.encodebytes(image.getvalue())
