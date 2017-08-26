from django.conf.urls import include,url
from django.contrib import admin

app_name = 'frontend'

urlpatterns = [

    # /admin/
    url(r'^admin/', admin.site.urls),

    # /
    url(r'^', include('frontend.urls')),
]

#admin configuration
admin.site.site_title = 'OpenEasier Administration'
admin.site.site_header = 'OpenEasier Administration'
