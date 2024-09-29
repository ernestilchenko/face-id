from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path

from .models import Webcam, Person
from .views import video_view


class CustomAdminSite(AdminSite):
    site_header = "administration"


class WebcamAdmin(admin.ModelAdmin):
    change_list_template = "admin/webcam/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('video/', self.admin_site.admin_view(video_view), name='webcam-video'),
        ]
        return custom_urls + urls


admin_site = CustomAdminSite(name="myadmin")
admin_site.register(Webcam, WebcamAdmin)
admin_site.register(Person)
