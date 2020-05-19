from django.urls import path
from .views import *

app_name = "api"

urlpatterns = [
	path('memes', memes, name='memes'),
	path('memes_scores', memes_scores, name='memes-scores'),
	path('memes_clusters', memes_clusters, name='memes-clusters'),
]
