from django.urls import path

from .admin import admin_site
from .views import *

urlpatterns = [
    path('admin/', admin_site.urls),
    path('video_feed/', video_feed, name='video_feed'),
    path('open_door/', open_door, name='open_door'),
    path('close_door/', close_door, name='close_door'),
]
