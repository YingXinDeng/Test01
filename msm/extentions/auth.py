import logging

from rest_framework.authentication import BaseAuthentication
import jwt
from jwt import exceptions
from django.conf import settings
from msm.models import AccountLogin
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.sessions.backends.db import SessionStore
import re
from rest_framework.response import Response
# 可以有三种返回值
# 抛出异常 后续不再执行
# 返回一个元祖包含两个值，request.user request.auth


class JwtHeaderParamsAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 首先拿到前端的标识key
        token = request.META.get("HTTP_AUTHORIZATION")
        key = request.META.get("HTTP_SESSIONKEY")
        # print("Session_key: ", request.META.get("HTTP_SESSIONKEY"))
        s = SessionStore(session_key=key.split('=')[1])
        current_url = request.path_info
        print("这是当前的URL", current_url)
        # print("token： ", token)
        for reg in settings.VALID_URL:
            if re.match(reg, current_url):
                return None
        flag = False
        # 如果当前url在权限列表里面
        # print(s[settings.SESSION_PERMISSION_URL_KEY])

        for item in s[settings.SESSION_PERMISSION_URL_KEY]:
            # 把匹配出来的列表变成字符串
            # print(re.findall(r"/(.+?)/", current_url))
            if ("".join(re.findall(r"/(.+?)/", current_url)) in item) or (current_url in item):
                flag = True
                break
        if not flag:
            print("没有匹配的URL")
            return Response({"URL不匹配无权访问："})
        else:
            payload = None
            msg = None
            salt = settings.SECRET_KEY
            try:
                payload = jwt.decode(token, salt, algorithms="HS256")
                # print(payload)
            except exceptions.ExpiredSignatureError:
                raise AuthenticationFailed({'code': 1003, 'error': 'Token 已失效'})
            except jwt.DecodeError:
                raise AuthenticationFailed({'code': 1003, 'error': 'Token 认证失败'})
            except jwt.InvalidTokenError:
                raise AuthenticationFailed({'code': 1003, 'error': '非法的 Token'})

            return (payload, token)
