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
from .noDbModel import AutoFollowResp
from django import forms
# これはすべてのファイルに書く
logger = getLogger(__name__)

# Create your views here.


class AutoFollowView():
    templates = 'page/base_twitter_auto_follow.html'
    temp_child = 'page/twitter_auto_follow.html'

    def twitter_api_link(request):
        request.session.clear()
        logger.debug("セッションをクリアしました")
        # カスタマーキー
        consumer_key = config.CONSUMER_KEY
        consumer_secret = config.CONSUMER_SECRET

        # リクエストトークン
        request_token_url = "https://api.twitter.com/oauth/request_token"

        # Twitter Application Management で設定したコールバックURLsのどれか
        oauth_callback = "http://http://apppy-tw-bat.com/mushapp/twitter_controller/"
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
        # response = twitter.fetch_request_token(access_token_url)
        response = twitter.post(
            access_token_url,
            params={'oauth_verifier': oauth_verifier}
        )

        # responseからアクセストークンを取り出す
        access_token = dict(parse_qsl(response.content.decode("utf-8")))
        # oauth_token = response.args.get('oauth_token')
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
                logger.debug("アクセストークンを更新しました")
        except OAuthTokenTemp.DoesNotExist:
            oAuthTokenTemp = OAuthTokenTemp()
            oAuthTokenTemp.user_id = access_token.get("user_id")
            oAuthTokenTemp.oauth_token = access_token.get("oauth_token")
            oAuthTokenTemp.oauth_token_secret = access_token.get(
                "oauth_token_secret")
            oAuthTokenTemp.save()
            logger.debug("アクセストークンを登録しました")
        request.session['oauth_token'] = oAuthTokenTemp.oauth_token
        request.session['oauth_token_secret'] = oAuthTokenTemp.oauth_token_secret
        # return render(request, 'auto_twitter', oAuthTokenTemp)
        return redirect('auto_twitter')

        # render(request, 'page/twitter_auto_follow.html', {'form': form})

    def auto_twitter(request):
        logger.info('Twitter自動フォロー画面を表示させます')
        form = TwitteAutoFollowForm()
        return render(request, AutoFollowView.templates, {'form': form})

    # データの検証
    def at_twitter_val_validation(request):
        if request.method == "POST":
            form = TwitteAutoFollowForm(data=request.POST)
            # データ正常
            if form.is_valid():
                if 'oauth_token' in request.session and 'oauth_token_secret' in request.session:
                    # ツイート検索キー
                    keyword = form.cleaned_data.get('keyword')
                    # フォロー数
                    maxFollowInt = form.cleaned_data.get('maxFollowInt')
                    # アクセストークン
                    AT = request.session['oauth_token']
                    AS = request.session['oauth_token_secret']
                    # フォロー処理
                    autoFollowRespList = TwitterUtil.auto_twt_follow(
                        keyword, maxFollowInt, AT, AS)
                    return render(request, AutoFollowView.temp_child, {'form': form, 'autoFollowRespList': autoFollowRespList})
                else:
                    logger.debug('セッションに登録がありません')
                    return redirect('twitter_api_link')
            # データ異常
            else:
                try:
                    form.clean_maxFollowInt()
                except forms.ValidationError:
                    return render(request, AutoFollowView.temp_child, {'form': form})


class TwitterUtil():

    def auto_twt_follow(keyword, maxFollowInt, AT, AS):

        # カスタマーキー
        CK = config.CONSUMER_KEY
        CS = config.CONSUMER_SECRET

        logger.info('TwitterAPI認証開始')
        auth = tweepy.OAuthHandler(CK, CS)
        auth.set_access_token(AT, AS)
        # インスタンス生成
        api = tweepy.API(auth, wait_on_rate_limit=True)
        logger.info('TwitterAPI認証終了')
        q = keyword
        count = maxFollowInt
        search_result = api.search(q=q, count=count)

        # フォローする人リスト
        autoFollowRespList = []

        for result in search_result:

            autoFollowResp = AutoFollowResp()
            # ユーザID取得
            username = result.user._json['screen_name']
            autoFollowResp.setScreenName(username)
            print("表示ユーザID：@{0}".format(username))
            # ツイートからユーザID取得
            user_id = result.id
            user = result.user.name
            autoFollowResp.setTweetId(user)
            tweet = result.text
            autoFollowResp.setTweetContent(tweet)
            time = result.created_at
            try:
                # api.create_favorite(user_id)
                # print("いいねしました")
                # api.retweet(user_id)
                # print("リツイートしました")
                api.create_friendship(username)
                msg = "フォローしました"
                logger.info(msg+" ID:"+username)
                autoFollowResp.setFollowResult(msg)
                autoFollowRespList.append(autoFollowResp)
            except:
                msg = "既にフォロー中"
                traceback.print_exc()
                logger.info(msg+" ID:"+username)
                autoFollowResp.setFollowResult(msg)
                autoFollowRespList.append(autoFollowResp)
        return autoFollowRespList
