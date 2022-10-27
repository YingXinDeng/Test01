from django.shortcuts import render
from rest_framework.views import APIView
from rbac import models as rbacmodels
from rest_framework.response import Response
from msm import models
import json
from django.http import JsonResponse
from msm.extentions.auth import JwtHeaderParamsAuthentication
import re


# check user if existed

class ExistUser(APIView):

    def post(self, request, *args, **kwargs):

        print("需要核对的前端用户信息", request.body)
        user = request.data.get("username")
        check = rbacmodels.UserInfo.objects.get(username=user)
        if check:
            return Response({'code': 209, 'data': user, 'check': 0, "message": "User is existed."})
        else:
            return Response({'code': 200, 'data': user, 'check': 1, "message": "You can use this username."})


# check account if existed

class ExistEmployeeCG(APIView):

    def post(self, request, *args, **kwargs):

        print("需要核对的换组用户名", request.body)
        user_or_id = request.data.get("name_id")
        if user_or_id:
            check = models.CheckinTable.objects.get(workid=user_or_id)
            if check:
                return Response({'code': 200, 'data': user_or_id, 'check': 0, "message": "User is existed."})
            else:
                return Response({'code': 299, 'data': user_or_id, 'check': 1, "message": "You can use this username."})


def checkname(request):
    if request.method == 'POST':

        res = json.loads(request.body)
        print(res)
        ok = res["name"]
        if res["flag"] == "name":
            left = ok.split(" ")[0]
            right = ok.split(" ")[1]
            if models.UserProfile.objects.filter(first_name=left, second_name=right, data_status=1).first():
                return JsonResponse({'code': 200, "check": 1})
            else:
                return JsonResponse({'code': 999, "check": 0})
        # 工号检验
        else:
            w = models.UserProfile.objects.filter(workid=ok, data_status=1).first()
            if w:
                return JsonResponse({'code': 200, "check": 1})
            else:
                return JsonResponse({'code': 999, "check": 0})


# 左侧菜单列表返回
class MenuData(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = {
            "version": "1.0",
            "code": 200,
            "data": []
        }

    def jsonText(self, obj):
        data = {
            "id": obj.id,
            "title": obj.title,
            "icon": obj.icon,
            "router": obj.router,
            "Subclass": []
        }
        return data

    def get(self, request):
        print(request.body)

        return JsonResponse(self.result)


# 获取组和mission的数据
class DepsApis(APIView):
    authentication_classes = [JwtHeaderParamsAuthentication, ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = {
            "version": "1.0",
            "code": 200,
            "data": []
        }

    def serialize(self, obj, flag='all'):
        if flag == 'all':
            mission = models.Department.objects.filter(dep_name=obj["dep_name"]).values("mission")
            m_list = [{
                "label": m["mission"],
                "value": m["mission"],
            } for m in mission]

            result = {
                "label": obj['dep_name'],
                "value": obj['dep_name'],
                "children": m_list
            }
        else:
            mission = models.Department.objects.filter(dep_name=obj).values("mission")
            m_list = [{
                "label": m["mission"],
                "value": m["mission"],
            } for m in mission]
            result = {
                "label": obj,
                "value": obj,
                "children": m_list
            }

        # print(result)
        return result

    def missionSerialize(self, obj):

        result = {
            "label": obj['mission'],
            "value": obj['mission']
        }
        return result

    def depNotExist(self, dep_id):
        self.result["code"] = 400
        self.result["data"].append("Not exist the data with id = {}".format(dep_id))

    def get(self, request):
        # print("解密出来的原数据", request.user)
        head_data = request.user
        if head_data:
            group_info = head_data.get('groups')
        # 目前只接受三种类型的角色
        # 超级管理员
        if group_info == "all":
            group_list = models.Department.objects.all().values("dep_name").distinct()
            self.result["data"] = [self.serialize(d) for d in list(group_list)]
        # 中间部门
        elif "," in group_info:
            group_set = group_info.split(',')
            gg = []
            for g in range(len(group_set)):
                gg.append(group_set[g])
            self.result["data"] = [self.serialize(d, "others") for d in gg]
        # 普通组长
        else:
            mission_list = models.Department.objects.filter(dep_name=group_info).values("mission")
            # print(list(mission_list))
            self.result["data"] = [self.missionSerialize(d) for d in list(mission_list)]

            # d_list = models.Department.objects.values("dep_name").distinct()
            #  print(d_list)
            # self.result["data"] = [self.serialize(d) for d in d_list]

        return JsonResponse(self.result)


class CheckinList(APIView):
    authentication_classes = [JwtHeaderParamsAuthentication, ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = {
            "version": "1.0",
            "code": 200,
            "data": [],
            "message": "Success !"
        }

    def serialize(self, obj):
        mission = models.Department.objects.filter(dep_name=obj["dep_name"]).values("mission")
        m_list = [{
            "label": m["mission"],
            "value": m["mission"],
        } for m in mission]

        result = {
            "label": obj['dep_name'],
            "value": obj['dep_name'],
            "children": m_list
        }

        return result

    def get(self, request):

        group_list = models.Department.objects.all().values("dep_name").distinct()
        self.result["data"] = [self.serialize(d) for d in list(group_list)]

        return JsonResponse(self.result)
