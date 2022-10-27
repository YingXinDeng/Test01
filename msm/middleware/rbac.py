from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from rest_framework.response import Response
from django.shortcuts import render, redirect, HttpResponse
import importlib


class RbacMiddleware(MiddlewareMixin):
    """
    权限控制中间件
    """
    def process_request(self, request):
        from django.shortcuts import HttpResponse
        sessionkey = request.META.get("sessionkey")

        s = SessionStore()

        # 获取当前请求url
        current_url = request.path_info

        if current_url != "/login/":
        # 获取当前用户中所有的session
            # permission_list = request.session.get(settings.PERMISSION_SESSION_KEY)
            url = request.session.get(settings.SESSION_PERMISSION_URL_KEY, 0)

            if not url:
                return None
            print("这是权限列表2", url)
        # 进行权限的比对

    def process_response(self, request, response):
        print('自定义逻辑')
        return response

    def process_view(self, request, view_func, view_func_args, view_func_kwargs):
        print('M2.process_view')


