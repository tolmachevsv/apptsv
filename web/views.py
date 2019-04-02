from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse
from django.template import loader

import requests
import datetime
import vk

access_token_cookie = 'vk_access_token'
user_id_cookie = 'vk_user_id'

client_id = 6920486
secure_key = 'eIKDzRe3DyZrZIZEfdpz'
redirect_uri = 'https://apptsv.herokuapp.com/auth'

friends_count = 5
fields = 'nickname, domain, sex, bdate, city, country, timezone'



def index(request):
    if access_token_cookie not in request.COOKIES:
        template = loader.get_template('web/index.html')
        return HttpResponse(template.render({}, request))

    return HttpResponseRedirect("/info")


def auth_with_code(request):
    code = request.GET.get('code', None)
    if not code:
        return HttpResponseNotFound("Code not found")

    token, user_id = get_access_token(code)
    if not token:
        return HttpResponseNotFound("Error while receiving token")

    response = HttpResponseRedirect("/info")
    set_cookie(response, access_token_cookie, token)
    set_cookie(response, user_id_cookie, user_id)

    return response


def info(request):
    if access_token_cookie not in request.COOKIES:
        return HttpResponseNotFound("Access token not found in request, are you authenticated?")
    if user_id_cookie not in request.COOKIES:
        return HttpResponseNotFound("User id not found in request, are you authenticated?")

    token = request.COOKIES[access_token_cookie]
    user_id = request.COOKIES[user_id_cookie]

    return render_info_page(token, user_id, request)


def render_info_page(token, user_id, request):
    session = vk.Session(access_token=token)
    api = vk.API(session, v=5)

    user = api.users.get(user_ids=user_id)
    friends = api.friends.get(user_id=user_id, order='random', count=friends_count, fields=fields)

    print(user)
    print(friends)

    template = loader.get_template('web/friends.html')

    return HttpResponse(template.render({
        'friends': friends['items'],
        'user': user[0]
    }, request))


def vk_redirect(request):
    resp_type = 'code'
    scope = 'friends'
    url = 'https://oauth.vk.com/authorize?client_id={}&redirect_uri={}&response_type={}&scope={}&v=5.92'.format(
        client_id, redirect_uri, resp_type, scope
    )
    return HttpResponseRedirect(url)


def get_access_token(code):
    url = "https://oauth.vk.com/access_token?client_id={}&client_secret={}&redirect_uri={}&code={}".format(
        client_id, secure_key, redirect_uri, code
    )
    resp = requests.get(url)

    data = resp.json()
    if "error" in data:
        return None, None

    return data['access_token'], data['user_id']


def set_cookie(response, key, value, days_expire = 1):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  #one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires)
