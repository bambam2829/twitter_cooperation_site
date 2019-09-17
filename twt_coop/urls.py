from django.conf.urls import include, url
from .views import AutoFollowView

urlpatterns = [
    url(r'^mushapp$', AutoFollowView.twitter_api_link, name='twitter_api_link'),
    url(r'^mushapp/twitter_controller/*',
        AutoFollowView.twitter_controller, name='twitter_controller'),
    url(r'^mushapp/twitter_api$', AutoFollowView.auto_twitter, name='auto_twitter'),
    #url('', views.auto_twt_follow, name='auto_twt_follow'),
    url('', AutoFollowView.at_twitter_val_validation,
        name='at_twitter_val_validation'),
]
