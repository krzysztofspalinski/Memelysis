from django.urls import path
from .views import index, about, analytics

urlpatterns = [
	path('', index, name="index"),
	path('about', about, name="about"),
	path('analytics', analytics, name="analytics")
]
