from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

app_name = 'frontend'

urlpatterns = [

    # /
    url(r'^$',
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name='login'),

    # /logout/
    url(r'^logout/$',
        auth_views.LogoutView.as_view(),
        name='logout'),

    # /index/resources/panel/
    url(r'^index/resources/$',
        views.ResourcePanelView.as_view(),
        name='panel_resource'),

    # /index/resource/
    url(r'^index/resource/$',
        views.ResourceSearchView.as_view(),
        name='add_resource'),

    # /index/resource/produtor/columns
    url(r'^index/resource/(?P<table_name>[a-z_]+)/columns/$',
        views.ResourceColumnsView.as_view(),
        name='columns_resource'),

    # /index/resource/produtor/columns
    url(r'^index/resource/(?P<table_name>[a-z_]+)/create/$',
        views.ResourceCreateView.as_view(),
        name='create_resource'),

]
