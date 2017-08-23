from django.conf.urls import include,url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls)
]

#admin configuration
admin.site.site_title = 'OpenEasier Administration'
admin.site.site_header = 'OpenEasier Administration'