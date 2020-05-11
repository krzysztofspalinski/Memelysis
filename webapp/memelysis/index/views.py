from django.shortcuts import render
from .models import Memes
from .utils import get_distribution_plot


def index(request):
    memes = Memes.objects.all().order_by('-meme_datetime')[:5]
    for meme in memes:
        meme_score = meme.memesupvotesstatistics.upvotes
        meme_source = meme.source.name
        dist_plot = get_distribution_plot(
            meme_score, meme_source).decode('utf8')
        image_data = f"data:image/png;base64,{dist_plot}"
        meme.image_data = image_data
    return render(request, 'index/home.html', context={'memes': memes})
