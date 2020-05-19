from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('api/', include(('api.urls', 'api'), namespace='api')),
    path('', include('index.urls')),
    path('admin/', admin.site.urls)
]
