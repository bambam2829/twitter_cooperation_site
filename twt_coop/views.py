from django.shortcuts import redirect
from requests_oauthlib import OAuth1Session
from urllib.parse import parse_qsl
from . import config
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def post_list(request):
    # カスタマーキー
    consumer_key = config.CONSUMER_KEY
    consumer_secret = config.CONSUMER_SECRET

    # リクエストトークン
    request_token_url = "https://api.twitter.com/oauth/request_token"
    #oauth_token = request.GET["oauth_token"]
    #oauth_verifier = request.GET["oauth_verifier"]


    # Twitter Application Management で設定したコールバックURLsのどれか
    oauth_callback = "http://18.191.1.21/"

    twitter = OAuth1Session(consumer_key, consumer_secret)

    response = twitter.post(
        request_token_url,
        params={'oauth_callback': oauth_callback}
    )
#raise ValueError("error!")
    # responseからリクエストトークンを取り出す
    request_token = dict(parse_qsl(response.content.decode("utf-8")))

    # リクエストトークンから連携画面のURLを生成
    authenticate_url = "https://api.twitter.com/oauth/authenticate"
    authenticate_endpoint = '%s?oauth_token=%s' \
        % (authenticate_url, request_token['oauth_token'])
    result = {'result' : authenticate_endpoint}

    return redirect(authenticate_endpoint)
    # return render(request, 'blog/post_list.html',result)
