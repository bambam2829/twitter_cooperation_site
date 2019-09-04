from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^mysite/$', views.twitter_api_link, name='twitter_api_link'),
    url(r'^mysite/twitter_controller/*',
        views.twitter_controller, name='twitter_controller'),
    url(r'^mysite/twitter_api/$', views.auto_twitter, name='auto_twitter'),
    url('', views.auto_twt_follow, name='auto_twt_follow'),
]
