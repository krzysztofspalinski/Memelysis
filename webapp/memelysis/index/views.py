from django.shortcuts import render
from .models import Memes


def index(request):
    memes = Memes.objects.all()
    return render(request, 'index/home.html', context={'memes': memes})
