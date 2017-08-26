from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import ResourcePanelView, ResourceSearchView

urlpatterns = [

    # /
    url(r'^$',
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name='login'),

    # /logout/
    url(r'^logout/$',
        auth_views.LogoutView.as_view(),
        name='logout'),

    # /index/resources/
    url(r'^index/resources/$',
        ResourcePanelView.as_view(),
        name='list_resource'),

    # /index/resources/
    url(r'^index/resource/$',
        ResourceSearchView.as_view(),
        name='add_resource'),

]
