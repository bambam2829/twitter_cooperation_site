from django.shortcuts import redirect
from requests_oauthlib import OAuth1Session
from urllib.parse import parse_qsl
from . import config
from django.shortcuts import render
from django.http import HttpResponse
from logging import basicConfig, getLogger, DEBUG
from twt_coop.models import OAuthTokenTemp
import traceback
import tweepy
from .forms import TwitteAutoFollowForm

# これはメインのファイルにのみ書く
basicConfig(level=DEBUG)
# これはすべてのファイルに書く
logger = getLogger(__name__)

# Create your views here.


def twitter_api_link(request):
    # カスタマーキー
    consumer_key = config.CONSUMER_KEY
    consumer_secret = config.CONSUMER_SECRET

    # リクエストトークン
    request_token_url = "https://api.twitter.com/oauth/request_token"

    # Twitter Application Management で設定したコールバックURLsのどれか
    oauth_callback = "http://127.0.0.1:8000/mysite/twitter_controller/"
    # oauth_callback = "http://18.191.1.21/"
    twitter = OAuth1Session(consumer_key, consumer_secret)

    response = twitter.post(
        request_token_url,
        params={'oauth_callback': oauth_callback}
    )
# raise ValueError("error!")
    # responseからリクエストトークンを取り出す
    request_token = dict(parse_qsl(response.content.decode("utf-8")))

    # リクエストトークンから連携画面のURLを生成
    authenticate_url = "https://api.twitter.com/oauth/authenticate"
    authenticate_endpoint = '%s?oauth_token=%s' \
        % (authenticate_url, request_token['oauth_token'])
    result = {'result': authenticate_endpoint}

    return redirect(authenticate_endpoint)
    # return render(request, 'blog/twitter_api_link.html',result)


def twitter_controller(request):
    logger.debug("*************************")
    # カスタマーキー
    consumer_key = config.CONSUMER_KEY
    consumer_secret = config.CONSUMER_SECRET
    # アクセストークン生成用
    oauth_token = request.GET["oauth_token"]
    oauth_verifier = request.GET["oauth_verifier"]

    twitter = OAuth1Session(
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_verifier,
    )
    access_token_url = "https://api.twitter.com/oauth/access_token"
    #response = twitter.fetch_request_token(access_token_url)
    logger.debug('************************:aaaaaaaaaaaaaaaaaaaaaaaa')

    response = twitter.post(
        access_token_url,
        params={'oauth_verifier': oauth_verifier}
    )

    # responseからアクセストークンを取り出す
    access_token = dict(parse_qsl(response.content.decode("utf-8")))
    #oauth_token = response.args.get('oauth_token')
    logger.debug('************************:aaaaaaaaaaaaaaaaaaaaaaaa')
    try:
        oAuthTokenTemp = OAuthTokenTemp.objects.get(
            user_id=access_token.get("user_id"))
        if oAuthTokenTemp.oauth_token != access_token.get("oauth_token"):
            oAuthTokenTemp.user_id = access_token.get("user_id")
            oAuthTokenTemp.oauth_token = access_token.get("oauth_token")
            oAuthTokenTemp.oauth_token_secret = access_token.get(
                "oauth_token_secret")
            oAuthTokenTemp.save()
            request.session['oauth_token'] = oAuthTokenTemp.oauth_token
            request.session['oauth_token_secret'] = oAuthTokenTemp.oauth_token_secret
            logger.debug("アクセストークンを更新しました。")
    except OAuthTokenTemp.DoesNotExist:
        oAuthTokenTemp = OAuthTokenTemp()
        oAuthTokenTemp.user_id = access_token.get("user_id")
        oAuthTokenTemp.oauth_token = access_token.get("oauth_token")
        oAuthTokenTemp.oauth_token_secret = access_token.get(
            "oauth_token_secret")
        oAuthTokenTemp.save()
        logger.debug("アクセストークンを登録しました。")
    request.session['oauth_token'] = oAuthTokenTemp.oauth_token
    request.session['oauth_token_secret'] = oAuthTokenTemp.oauth_token_secret
    # return render(request, 'page/auto_twitter.html')
    return redirect('auto_twitter')


def auto_twt_follow(request):
    if request.method == "POST":
        form = TwitteAutoFollowForm(data=request.POST)
        if form.is_valid():
            q = form.cleaned_data.get('keyword') # ツイート検索キー
            count = form.cleaned_data.get('maxFollowInt')  # 取得数
            if 'oauth_token' in request.session and 'oauth_token_secret' in request.session:
                # カスタマーキー
                CK = config.CONSUMER_KEY
                CS = config.CONSUMER_SECRET

                # アクセストークン
                AT = request.session['oauth_token']
                AS = request.session['oauth_token_secret']

                auth = tweepy.OAuthHandler(CK, CS)
                auth.set_access_token(AT, AS)
                logger.debug('認証できてる？？？？？？？？？？？？？？？？？')
                # インスタンス生成
                api = tweepy.API(auth)
                search_result = api.search(q=q, count=count)

                for result in search_result:
                    # ユーザID取得
                    username = result.user._json['screen_name']
                    print("")
                    print("")
                    print("表示ユーザID：@{0}".format(username))
                    # ツイートからユーザID取得
                    user_id = result.id
                    print("ツイートID：{0}".format(user_id))
                    user = result.user.name
                    print("ユーザ名：{0}".format(user))
                    tweet = result.text
                    print("***************************ツイート内容*******************************")
                    print(tweet)
                    print("********************************************************************")
                    time = result.created_at
                    print(time)
                    try:
                        api.create_favorite(user_id)
                        print("いいねしました")
                        # api.retweet(user_id)
                        # print("リツイートしました")
                        api.create_friendship(username)
                        print("フォローしました")
                    except:
                        traceback.print_exc()
                        print("既にフォロー中")
                return redirect('auto_twitter')
            else:
                logger.debug('クッキーに登録されてない')
                return redirect('twitter_api_link')
    else:
        form = TwitteAutoFollowForm()
    return render(request, 'page/auto_twitter.html', {'form': form})
            # return render(request, 'page/auto_twitter.html', api)


def auto_twitter(request):
    logger.debug('画面を表示させます')
    form = TwitteAutoFollowForm()
    return render(request, 'page/auto_twitter.html', {'form': form})
