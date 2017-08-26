from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # /
    url(r'^$',
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name='login'),

    # /
    url(r'^logout/$',
        auth_views.LogoutView.as_view(),
        name='logout'),

    # /index/resources/
    url(r'^index/resources/$', views.index, name='resources'),

]
