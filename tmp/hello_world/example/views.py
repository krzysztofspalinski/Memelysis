from django.shortcuts import render
from django.http import HttpResponse
from hello_world.settings import DATABASES

# Create your views here.


def hello_world(request):
    return HttpResponse("Hello World! Zmiana bazy danych" + str(DATABASES))
