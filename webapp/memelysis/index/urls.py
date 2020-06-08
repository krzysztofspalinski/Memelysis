from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="index"),
    path('about', about, name="about"),
    path('analytics', analytics, name="analytics"),
    path('get_graph', get_graph, name="get-graph"),
    path('sort', sort, name="sort"),
    path('select_category', select_category, name="soselect-category"),
]
