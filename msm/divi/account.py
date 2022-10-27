from rest_framework.views import APIView
from rbac import models
from rest_framework.response import Response
from msm.outils.jwt_token import creat_token
from django.conf import settings
from rbac.service.init_permission import init_permission
from msm.models import Department
from django.http import JsonResponse
from django.views import View
from msm.extentions.auth import JwtHeaderParamsAuthentication
from importlib import import_module
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import render, redirect, HttpResponse


class Authoaccount(APIView):
    authentication_classes = []

    def jsonText(self, obj):
        data = {
            "id": obj.id,
            "title": obj.title,
            "icon": obj.icon,
            "router": obj.router,
            "Subclass": []
        }
        return data

    def post(self, request, *args, **kwargs):

        # print(request.body)
        user = request.data.get('account')
        pwd = request.data.get("password")
        # print(user, pwd)
        user_obj = models.UserInfo.objects.filter(username=user, password=pwd).first()
        if not user_obj:
            return Response({'code': 1000, 'error': 'username or password is not right'})
        # 获取用户信息和权限写入session
            # 获取当前用户所拥有的所有角色    "id", 'title',
        else:
            init_permission(request, user_obj)  # 调用init_permission，初始化权限
        # url_list = user_obj.roles.filter(permissions__url__isnull=False).values('permissions__url').distinct()
            request.session.save()
            key = request.session.session_key
            token = creat_token({'id': user_obj.id, 'user': user_obj.username, 'groups': user_obj.nickname})
            # 菜单数据生成
            menu_data = []
            for m in request.session[settings.SESSION_PERMISSION_MENU_KEY]:
                menu_obj = models.Menu.objects.filter(id=m).first()
                menu_data.append(self.jsonText(menu_obj))

            if key and token:
                # 把key发给前端保存
                return Response({'code': 200, 'data': token, 'cookie': key, 'role': user_obj.nickname,
                                 "menu": menu_data})
            else:
                return Response({'code': 400, "error": "Server has a problem !! "})


class DepsApisssss(APIView):
    # authentication_classes = [JwtHeaderParamsAuthentication, ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = {
            "version": "1.0",
            "code": 200,
            "data": []
        }

    def serialize(self, obj):
        result = {
            "label": obj.dep_name,
            "value": obj.dep_name
        }
        return result

    def depNotExist(self, dep_id):
        self.result["code"] = 400
        self.result["data"].append("Not exist the data with id = {}".format(dep_id))

    def get(self, request, d_id=0):

        if d_id:
            print(d_id)
            dep = Department.objects.filter(id=int(d_id)).first()
            # dep = Department.objects.get(id=int(d_id))
            if dep:
                print(dep)
                self.result["data"].append(self.serialize(dep))
            else:
                self.result["code"] = 400
                self.result["data"].append("Not exist the data with id = {}".format(d_id))
        else:
            print("URL列表：", request.session.get(settings.SESSION_PERMISSION_URL_KEY))
            d_list = Department.objects.all()
            self.result["data"] = [self.serialize(d) for d in d_list]

        return JsonResponse(self.result)


