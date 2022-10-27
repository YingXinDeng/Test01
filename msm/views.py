from django.shortcuts import render
import pymysql
# Create your views here.
import time
import base64
import os
import re
from datetime import date, datetime
from datetime import timedelta
from django.db.models import Count
import django.utils.timezone as timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dj.settings import MEDIA_ROOT, WEB_HOST_MEDIA_URL
from django.shortcuts import render, redirect, HttpResponse

from msm import models
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core import serializers
import json
from .models import AccountLogin
from rest_framework import viewsets
from msm.models import AccountLogin
from msm.serializer import UserLoginSerializer

from rest_framework.views import APIView
# Create your views here.

from django import forms
# 测试的视图方法

from django.core.files.base import ContentFile

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator, decorator_from_middleware
from msm.models import Department
from msm.models import CheckinTable
from msm.models import UserProfile
from msm.models import SubMenu
from msm.models import ChangeGroup
# 认证模块
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
# 对应数据库
from django.contrib.auth.models import User
from django.http.multipartparser import MultiPartParser
from django.http import QueryDict
from msm.extentions.auth import JwtHeaderParamsAuthentication
from msm.outils.jwt_token import creat_token
from rest_framework.decorators import authentication_classes
from django.conf import settings


def companydata(request):
    result = {
        "version": "1.0",
        "code": 200,
        "data": [],
        "message": "Success !"
    }
    if request.method == 'GET':
        comp = models.CompanyType.objects.values("com_name")
        print(comp)

        for co in list(comp):
            company_list = {
                "label": co["com_name"],
                "value": co["com_name"],
            }
            result["data"].append(company_list)

        return JsonResponse(result)


class Autho(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        # print(request.body)
        user = request.data.get('account')
        pwd = request.data.get("password")
        # print(user, pwd)
        user_object = models.AccountLogin.objects.filter(account_num=user, account_password=pwd).first()
        if not user_object:
            return Response({'code': 1000, 'error': 'username or password is not right'})
        token = creat_token({'id': user_object.id, 'user': user_object.account_num})
        return Response({'code': 200, 'data': token})


class ProOrder(APIView):
    authentication_classes = [JwtHeaderParamsAuthentication, ]

    def get(self, request, *args, **kwargs):

        print("解密出来的原数据", request.user)
        head_data = request.user
        if head_data:
            user_id = head_data.get("id")
            user_name = head_data.get('user')
        #try:
            # user = models.AccountLogin.objects.get(account_num=user_name)

        return Response("显示出来了")


# loginin class


class Users:
    @staticmethod
    def get_status(request):
        if request.user.is_authenticated:
            return JsonResponse({
                "status": 0,
                "username": str(request.user)
            })
        else:
            return JsonResponse({
                "status": 1
            })

    @staticmethod
    def login_user(request):
        request_origin = request.META["HTTP_ORIGIN"]
        print(request_origin)
        if request.method == "POST":
            data = json.loads(request.body)
            print(data)
            username = data.get("account")
            password = data.get("password")
            result = {
                "version": "1.0",
                "code": 200,
                "data": [],
                "message": "Success !",
                "status": 0
            }
            if username is not None and password is not None:
                islogin = authenticate(request, username=username, password=password)
                if islogin:
                    login(request, islogin)
                    result["message"] = "Login Success"
                    result["username"] = username

                else:
                    result["status"] = 1
                    result["message"] = "Login not Success "
            else:
                result["status"] = 2
                result["message"] = "Parametere Error !!!"

            return JsonResponse(result)

    @staticmethod
    def logout_user(request):
        logout(request)
        return JsonResponse({
            "status": 0
        })
# 数据分析的处理函数


@method_decorator(csrf_exempt, "dispatch")
class chartView(View):

    def __init__(self, *args, **kwargs):
        super(chartView, self).__init__(*args, **kwargs)
        self.result = {
            "version": "1.0",
            "code": 200,
            "data": [],
            "message": "Success !"
        }

    def serialize(self, obj):
        dep = obj.dep_name
        d_name = dep.dep_name
        result = {
            "time": obj.join_time,
            "endtime": obj.end_time,
            "name": obj.first_name + ' ' + obj.second_name,
            "sex": obj.get_gender_display(),
            "workid": obj.workid,
            "group": d_name,
            "contract": obj.get_contract_type_display(),
            "birthday": obj.birthday,
            "mobile": obj.mobile,
            "address": obj.address,
        }
        return result

    def notexist(self, ct_id):
        self.result["code"] = 400
        self.result["data"].append("Not exist the data with id = {}".format(ct_id))

    def timeformat(self, stringtime):
        year = int(stringtime.split('-')[0])
        month = int(stringtime.split('-')[1])
        day = int(stringtime.split('-')[2])
        return date(year, month, day)

    def get(self, request):

        user_g = UserProfile.objects.values('dep_name').annotate(total=Count('id'))
        user_group = list(user_g)

        if user_group:
            self.result["data"] = user_group

        else:
            self.result["code"] = 400
            self.result["data"].append("No data inside!")

       # uid = UserProfile.objects.get(id=int(ct_id))
       # print(uid)
        # did = Department.objects.filter(id=int(ct_id)).first()
        #did = Department.objects.get(id=int(ct_id))
        #ct_ = CheckinTable(arr_time="357369443", lea_time="357369443")
       # ct_.save()
        # page = request.GET.get('page')
        # if page:
            # page = int(page)
            # start = (page - 1) * 10
            #end = page*10
            #d_list = CheckinTable.objects.all()[start:end]

        #else:
         #   self.result["code"] = 400
          #  self.result["data"].append("No data inside!")

        return JsonResponse(self.result)


# 获取二级菜单数


# 部门或者组信息的菜单返回

@method_decorator(csrf_exempt, "dispatch")
class DepsApis(APIView):
    authentication_classes = [JwtHeaderParamsAuthentication, ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = {
            "version": "1.0",
            "code": 200,
            "data": []
        }

    def serialize(self, obj):
        result = {
            "label": obj['dep_name'],
            "value": obj['dep_name']
        }
        return result

    def depNotExist(self, dep_id):
        self.result["code"] = 400
        self.result["data"].append("Not exist the data with id = {}".format(dep_id))

    def get(self, request, d_id=0):
        # print("URL列表：", request.session.get(settings.SESSION_PERMISSION_URL_KEY))
        print(request.user)
        # 目前只接受三种类型的角色
        if d_id != 0:
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

            d_list = Department.objects.values("dep_name").distinct()
            #  print(d_list)
            self.result["data"] = [self.serialize(d) for d in d_list]

        return JsonResponse(self.result)

    def post(self, request):
        try:
            d = Department()

        except Exception as e:
            self.result["code"] = 500
            self.result["data"].append(str(e))
        else:
            self.result["data"].append(self.serialize(d))
        return JsonResponse(self.result)

    def put(self, request, d_id):

        dep = Department.objects.filter(id=int(d_id)).first()
        if dep:
            # put = QueryDict(request.body)  // 局限性
            # put_data = put[0]    # put_data = put_data.get("d.dep_name")
            # print(put[0])
            try:
                d = MultiPartParser(request.META, request, request.upload_handlers).perse()
            except Exception as e:
                self.result["code"] = 500
                self.result["data"].append(str(e))
            else:
                self.result["data"].append(self.serialize(d))
        else:
            self.result["code"] = 400
            self.result["data"].append("Not exist the data with id = {}".format(d_id))
        return JsonResponse(self.result)

    def delete(self, request, d_id):
        return JsonResponse(self.result)


@method_decorator(csrf_exempt, "dispatch")
class CheckIn(APIView):

    def __init__(self, *args, **kwargs):
        super(CheckIn, self).__init__(*args, **kwargs)
        self.result = {
            "version": "1.0",
            "code": 200,
            "data": [],
            "message": "Success!"
        }

    def serialize(self, obj):
        print(str(obj.workid))
        print(str(obj.workid_id))
        u = UserProfile.objects.filter(workid=obj.workid_id).first()
        if obj.tags == 0:
            print("_______________")
            arr_pho = ""
            lea_pho = ""
        elif obj.tags == 1:
            arr_pho = "http://127.0.0.1:8000/media/photos" + re.search(r"photos(.*)", str(obj.arr_photo.url)).group(1)
            lea_pho = ""
        elif obj.tags == 2:
            lea_pho = "http://127.0.0.1:8000/media/photos" + re.search(r"photos(.*)", str(obj.lea_photo.url)).group(1)
            arr_pho = "http://127.0.0.1:8000/media/photos" + re.search(r"photos(.*)", str(obj.arr_photo.url)).group(1)
        elif obj.tags == 3:
            lea_pho = "http://127.0.0.1:8000/media/photos" + re.search(r"photos(.*)", str(obj.lea_photo.url)).group(1)
            arr_pho = ""

        result = {
            "day": obj.date_today,
            "workid": obj.workid_id,
            "name": u.first_name + ' ' + u.second_name,
            "arr_time": obj.arr_time,
            "lea_time": obj.lea_time,
            "picture": arr_pho,
            "lea_picture": lea_pho,
        }
        # print(result)
        return result

    def cgserialize(self, obj):
        # print(obj.cg_workid_id)
        u = UserProfile.objects.filter(workid=obj.cg_workid_id).first()
        sg = Department.objects.filter(id=obj.start_group_id).first()
        eg = Department.objects.filter(id=obj.finish_group_id).first()
        result = {
            "day": obj.date_today,
            "workid": obj.cg_workid_id,
            "name": u.first_name + ' ' + u.second_name,
            "start_time": obj.start_time,
            "finish_time": obj.finish_time,
            "start_group": sg.dep_name,
            "finish_group": eg.dep_name,
        }
        return result

    def notexist(self, ct_id):
        self.result["code"] = 400
        self.result["data"].append("Not exist the data with id = {}".format(ct_id))

    def timeformat(self, stringtime):
        year = int(stringtime.split('-')[0])
        month = int(stringtime.split('-')[1])
        day = int(stringtime.split('-')[2])
        return date(year, month, day)

    def changeNull(self, obj):
        if obj == "[]" or obj == "" or obj == "" or obj is None:
            return obj == ""

    def get(self, request):
        tab = request.GET.get('tab')
        group = request.GET.get('group')
        to_group = request.GET.get('to_group')
        search_time = request.GET.get('search_time')

        print(group)
        print(to_group)
        print(tab)
        # 时间为空的情况

        if search_time != "[]":
            start_date = self.timeformat(search_time[2:12])
            end_date = self.timeformat(search_time[15:25])

        else:
            start_date = ""
            end_date = ''

        if group is None:
            group = ""
            tag = 1
        if to_group is None:
            to_group = ""
            tag = 2

        to_m_list = Department.objects.filter(dep_name=to_group)
        m_list = Department.objects.filter(dep_name=group)

        # 换组查询
        if tab == "second" and tag == 1:
            print("这里是changeGroup")
            print(to_m_list)
            print(m_list)
        elif tab == "second" and tag == 2:
            cg = ChangeGroup.objects.filter(start_group__in=m_list, finish_group__in=to_m_list, date_today__range=(start_date, end_date))
            print(cg)
            if cg:
                self.result["data"] = [self.cgserialize(d) for d in cg]
            else:
                self.result["code"] = 400
                self.result["data"].append("No data inside!")
        # 签到中心查询
        else:
            print("这里是checkin")
            # 有时间选择的情况
            c_list = CheckinTable.objects.filter(group__in=m_list, date_today__range=(start_date, end_date))
            if c_list:
                self.result["data"] = [self.serialize(d) for d in c_list]
            else:
                self.result["code"] = 400
                self.result["data"].append("No data inside!")

            # page = int(page)
            # start = (page - 1) * 10
            # end = page*10
            # d _list = CheckinTable.objects.all()[start:end]

        return JsonResponse(self.result)

    def post(self, request):

        request_data = request.POST
        ct = CheckinTable()
        ct.arr_time = request_data.get("arr_time")
        ct.lea_time = request_data.get("lea_time")
        ct.arr_photo = request_data.get("picture")
        ct.lea_photo = request_data.get("lea_picture")
        try:
            ct.save()
        except Exception as e:
            self.result["code"] = 500
            self.result["data"].append(str(e))
        else:
            self.result["data"].append(self.serialize(ct))
        return JsonResponse(self.result)

    def put(self, request, ct_id):
        ct = CheckinTable.objects.filter(id=int(ct_id)).first()
        if ct:
            # put = QueryDict(request.body)  // 局限性
            # put_data = put[0]    # put_data = put_data.get("d.dep_name")
            # print(put[0])
            try:
                ct = MultiPartParser(request.META, request, request.upload_handlers).perse()
            except Exception as e:
                self.result["code"] = 500
                self.result["data"].append(str(e))
            else:
                self.result["data"].append(self.serialize(ct))
        else:
            self.result["code"] = 400
            self.result["data"].append("Not exist the data with id = {}".format(ct_id))
        return JsonResponse(self.result)

    def delete(self, request, ct_id):
        ct = CheckinTable.objects.filter(id=int(ct_id)).delete()
        if ct:
            ct.delete()
        return JsonResponse(self.result)


# 加班的

@csrf_exempt
@authentication_classes([JwtHeaderParamsAuthentication, ])
def overwork(request):
    result = {
        "version": "1.0",
        "code": 200,
        "data": [],
        "message": "Success !"
    }
    if request.method == 'GET':
        group_name = request.GET.get('group')
        # print(group_name)
        if group_name is None:
            over = models.ExternalWork.objects.filter(ex_data_status=True).order_by("-ex_long_time")
        else:
            g = Department.objects.filter(dep_name=group_name).first()
            over = models.ExternalWork.objects.filter(ex_group_id=g.id, ex_data_status=True)

        for o in over:
            # print(o.ex_long_time)
            # u = UserProfile.objects.filter(workid=o.workid).first()
            g = {
                    "workid": o.ew_workid_id,
                    "name": str(o.ew_workid),
                    "starttime": o.ex_start_time,
                    "endtime": o.ex_end_time,
                    "duration": o.ex_long_time,
                    "day": o.ex_work_date,
                }

            result["data"].append(g)

    if request.method == 'POST':
        res = json.loads(request.body)

        FMT = '%H:%M:%S'
        tdelta = datetime.strptime(res['time'][1], FMT) - datetime.strptime(res['time'][0], FMT)

        if tdelta.days < 0:
            tdelta = timedelta(
                days=0,
                seconds=tdelta.seconds,
                microseconds=tdelta.microseconds
            )

        tdelta = str(tdelta)
        # print(tdelta)
        hour = int(tdelta.split(':')[0])
        min = float(tdelta.split(':')[1])/60
        second = float(tdelta.split(':')[2]) / 60 / 60
        long_total = round(hour+min+second, 2)
        # print(long_total)

        gid = Department.objects.get(dep_name=res['in_group'])
        ornot = UserProfile.objects.filter(workid=res['workid']).first()
        # user = UserProfile.objects.get(workid=res['workid'])
        if ornot:
            user = UserProfile.objects.get(workid=res['workid'])
            over = models.ExternalWork(ew_workid=user,
                                       ew_name=res['name'],
                                       ex_group=gid,
                                       ex_work_date=res['date'],
                                       ex_start_time=res['time'][0],
                                       ex_end_time=res['time'][1],
                                       ex_long_time=long_total,
                                       ex_work_reason=res['reason'],
                                       ex_work_way=res['way']
                                       )
            over.save()
            result["message"] = "Successful get external work record !"
        else:
            result["code"] = 999
            result["message"] = "Workid is not exist, please try again !"

    return JsonResponse(result)


# 签到信息表格展示


class CheckinInfo(APIView):
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
        dep = obj.dep_name
        d_name = dep.dep_name
        result = {
            "time": obj.join_time,
            "endtime": obj.end_time,
            "name": obj.first_name + ' ' + obj.second_name,
            "sex": obj.get_gender_display(),
            "workid": obj.workid,
            "group": d_name,
            "contract": obj.get_contract_type_display(),
            "birthday": obj.birthday,
            "mobile": obj.mobile,
            "address": obj.address,
        }
        return result

    def table_serialize(self, obj):

        use = UserProfile.objects.filter(workid=obj.workid_id).first()
        if obj.tags == 0:
            arr_pho = ""
            lea_pho = ""
        elif obj.tags == 1:
            arr_pho = "http://127.0.0.1:8000/media/photos" + re.search(r"photos(.*)", str(obj.arr_photo.url)).group(1)
            lea_pho = ""
        elif obj.tags == 2:
            lea_pho = "http://127.0.0.1:8000/media/photos" + re.search(r"photos(.*)", str(obj.lea_photo.url)).group(1)
            arr_pho = "http://127.0.0.1:8000/media/photos" + re.search(r"photos(.*)", str(obj.arr_photo.url)).group(1)
        elif obj.tags == 3:
            lea_pho = "http://127.0.0.1:8000/media/photos" + re.search(r"photos(.*)", str(obj.lea_photo.url)).group(1)
            arr_pho = ""
        result = {
            "group": obj.group_id,
            "firstname": use.first_name,
            "secondname": use.second_name,
            "workid": obj.workid_id,
            "arr_time": obj.arr_time,
            "lea_time": obj.lea_time,
            # 图片返回的时候需要序列化
            "picture": arr_pho,
            "lea_picture": lea_pho,
            "mission": obj.group.mission
        }
        return result

    def employeeNotExist(self, e_id):
        self.result["code"] = 400
        self.result["data"].append("Not exist the data with id = {}".format(e_id))

    def get(self, request, group_mission):
        # 有组的时候作为get参数的时候是负责返回签到预备表数据的
        head_data = request.user
        if head_data:
            group_info = head_data.get('groups')
        print("-----------", group_mission)
        d_list = CheckinTable.objects.filter(date_today=date.today().__str__(), data_status=True)
        print("今天的数据在里面吗", d_list)
        if d_list:
            pass
        else:
            user_prof = UserProfile.objects.filter(data_status=True)
            for p in user_prof:
                print("需要打卡的员工")
                p_ = models.CheckinTable(
                    workid_id=p.workid,
                    group_id=p.dep_mission_id
                )
                p_.save()
        # checkin table 里面的下拉框的三种情况
        if group_mission == "all":
            # 页面一跳转来的时候就显示的列表
            # 目前只接受三种类型的角色
            # 超级管理员
            if group_info == "all":
                pass
            # 中间部门
            elif "," in group_info:

                group_set = group_info.split(',')
                gg = []
                for g in range(len(group_set)):
                    gg.append(group_set[g])
                g_id = Department.objects.filter(dep_name__in=list(gg))
                d_list = CheckinTable.objects.filter(date_today=date.today().__str__(), data_status=True, group_id__in=g_id)
            # 普通组长
            else:
                g_id = Department.objects.filter(dep_name=group_info)
                d_list = CheckinTable.objects.filter(date_today=date.today().__str__(), data_status=True, group_id__in=g_id)

        elif "," in group_mission:
            # 外键查询id
            group = group_mission.split(",")[0]
            mission = group_mission.split(",")[1]
            g_id = Department.objects.filter(dep_name=group, mission=mission).first()
            d_list = CheckinTable.objects.filter(date_today=date.today().__str__(), data_status=True, group_id=g_id)
        # 普通组长
        else:
            g_id = Department.objects.filter(mission=group_mission).first()
            d_list = CheckinTable.objects.filter(date_today=date.today().__str__(), data_status=True, group_id=g_id)

        self.result["data"] = [self.table_serialize(c) for c in d_list]

        return JsonResponse(self.result)

    def post(self, request):
        try:
            post_data = json.loads(request.body)
            det = UserProfile.objects.filter(workid=post_data['workid'])
            ci = CheckinTable.objects.filter(workid_id=post_data['workid'], date_today=date.today().__str__())
            det.delete()
            ci.delete()
            self.result["msg"] = "Deleted successfully !!"
        except Exception as e:
            self.result["code"] = 500
            self.result["data"].append(str(e))
            self.result["msg"] = "Failed to delete !!"
        return JsonResponse(self.result)


@method_decorator(csrf_exempt, "dispatch")
class EmployeeInfo(View):

    def __init__(self, *args, **kwargs):
        super(EmployeeInfo, self).__init__(*args, **kwargs)
        self.result = {
            "version": "1.0",
            "code": 200,
            "data": [],
            "message": "Success !"
        }

    def serialize(self, obj, flag):
        dep = obj.dep_mission
        comp = obj.company

        if flag:
            print(str(obj.get_gender_display()))
            result = {
                "time_value1": [obj.join_time, obj.end_time],
                "in_fname": obj.first_name,
                "in_sname": obj.second_name,
                "in_sex": str(obj.get_gender_display()),
                "in_workid": obj.workid,
                "in_group": [dep.dep_name, dep.mission],
                "in_company": comp.com_name,
                "in_contract": str(obj.get_contract_type_display()),
                "in_birthday": obj.birthday,
                "in_phone": obj.mobile,
                "in_adress": obj.address,
            }
        else:
            result = {
                "time": obj.join_time,
                "endtime": obj.end_time,
                "name": obj.first_name + ' ' + obj.second_name,
                "sex": obj.get_gender_display(),
                "workid": obj.workid,
                "group": dep.dep_name,
                "mission": dep.mission,
                "company": comp.com_name,
                "contract": obj.get_contract_type_display(),
                "birthday": obj.birthday,
                "mobile": obj.mobile,
                "address": obj.address,
            }
        return result

    def get(self, request):
        group = request.GET.get('group')
        workpk = request.GET.get('workid')
        # get_data = json.loads(request.body)
        flag = False
        if group is not None:
            g = Department.objects.filter(dep_name=group)
            for i in g:
                d_list = UserProfile.objects.filter(dep_mission_id=i.id, data_status=True).first()
                if d_list is None:
                    continue
                else:
                    self.result["data"].append(self.serialize(d_list, flag))
        elif workpk is not None:
            d_list = UserProfile.objects.filter(workid=workpk).first()
            flag = True
            self.result["data"] = [self.serialize(d_list, flag)]
        else:
            print("YES")
            d_list = UserProfile.objects.filter(data_status=1)
            print(d_list)
            self.result["data"] = [self.serialize(d, flag) for d in d_list]

        return JsonResponse(self.result)

    def post(self, request):
        try:
            post_data = json.loads(request.body)
            print(post_data)
            det = UserProfile.objects.filter(workid=post_data['workid'])
            det.update(data_status=False)
            # 进行删除操作的时候把数据状态变成不活跃，然后在相关联的加班表也把状态调整为不活跃
            ci = CheckinTable.objects.filter(workid_id=post_data['workid'])
            ci.update(data_status=False)
            change_status_ew = models.ExternalWork.objects.filter(ew_workid_id=post_data['workid'])
            change_status_ew.update(ex_data_status=False)
            # ci.delete()
            self.result["msg"] = "Delete successfully !!"
        except Exception as e:
            self.result["code"] = 500
            self.result["data"].append(str(e))
            self.result["msg"] = "Failed to delete !!"
        return JsonResponse(self.result)

    def put(self, request, e_id):
        dep = Department.objects.filter(id=int(e_id)).first()
        if dep:
            # put = QueryDict(request.body)  // 局限性
            # put_data = put[0]    # put_data = put_data.get("d.dep_name")
            # print(put[0])
            try:
                d = MultiPartParser(request.META, request, request.upload_handlers).perse()
            except Exception as e:
                self.result["code"] = 500
                self.result["data"].append(str(e))
            else:
                self.result["data"].append(self.serialize(d))
        else:
            self.result["code"] = 400
            self.result["data"].append("Not exist the data with id = {}".format(e_id))
        return JsonResponse(self.result)


# 员工信息添加 # 员工信息编辑

@csrf_exempt
@authentication_classes([JwtHeaderParamsAuthentication, ])
def AddEmployeeInfo(request):
    result = {
        "version": "1.0",
        "code": 200,
        "status": '',
        "data": [],
        "message": "Success !"
    }
    if request.method == 'POST':
        res = json.loads(request.body)
        print(res)
        # 性别判断
        if res['in_sex'] == "male":
            gender = 1
        elif res['in_sex'] == "female":
            gender = 2
        else:
            gender = 0

        # 合同类型判断
        if res['in_contract'] == "Temporary":
            contract = 3
        elif res['in_contract'] == "Trial":
            contract = 4
        elif res['in_contract'] == "CDD":
            contract = 2
        else:
            contract = 1
        # 外键查询id
        d_id = Department.objects.filter(dep_name=res['in_group'][0], mission=res['in_group'][1]).first()
        print(d_id)
        # 公司对象
        com = models.CompanyType.objects.filter(com_name=res['in_company']).first()
        # 如果工号已经存在，就更新数据
        u = UserProfile.objects.filter(workid=res['in_workid'])
        if u:
            print("!!!!!!!!!!!!!!!!")
            u.update(
                first_name=res['in_fname'],
                second_name=res['in_sname'],
                gender=gender,
                address=res['in_address'],
                mobile=res['in_phone'],
                join_time=res['time_value1'][0],
                end_time=res['time_value1'][1],
                company_id=com.id,
                contract_type=contract,
                dep_mission_id=d_id.id
                )

            result["message"] = "Data has been successfully modified ! "
        #  如果工号不存在
        else:
            #  先找到旧id的位置然后把状态改为不活跃的状态
            de = UserProfile.objects.filter(workid=res['stock_workid']).first()
            if de:
                UserProfile.objects.filter(id=de.id).update(data_status=False)
            # 插入新数据
            else:

                e = UserProfile(
                    workid=res['in_workid'],
                    first_name=res['in_fname'],
                    second_name=res['in_sname'],
                    gender=gender,
                    address=res['in_address'],
                    mobile=res['in_phone'],
                    join_time=res['time_value1'][0],
                    end_time=res['time_value1'][1],
                    company_id=com.id,
                    contract_type=contract,
                    dep_mission_id=d_id.id
                )
                print("有这个对象吗", e)
                if e:
                    e.save()
                    # 同时往签到表插入数据
                    p_ = models.CheckinTable(
                        workid_id=res['in_workid'],
                        group_id=d_id.id
                    )

                    p_.save()
                    result["message"] = "Data is successfully stocked !"
                else:
                    result['code'] = 400,
                    result["message"] = "Data is not successfully stocked"

    return JsonResponse(result)


# 签到列表的图片地址保存

@csrf_exempt
@authentication_classes([JwtHeaderParamsAuthentication, ])
def updateinfo(request):
    result = {
        "version": "1.0",
        "code": 200,
        "status": '',
        "data": [],
        "msg": '',
    }
    if request.method == 'POST':
        response = json.loads(request.body)
        # print(response)
        base64Imag = response['photo'].split(",")
        work_id = response['workid']  # 工号
        # img = base64Imag[1]
        # image_data = base64.b64decode(resultt)
        urls = ''
        IMAGE_ROOT = os.path.join(MEDIA_ROOT, 'photos/')
        dir_name = date.today().__str__().replace('-', '_', 2)  # 2019_06_21
        ds = os.path.join(IMAGE_ROOT, dir_name)  # 将日期作为目录名
        if response['arri_OR_leav'] == "arrive":
            tag = 1
            dirs = os.path.join(ds, 'arrive/')  # 加上是签到还是下班的签名
        else:
            if response['arrive_if_sign'] is None:
                # 未签到就只签退
                tag = 3
            else:
                # 有签到再进行签退
                tag = 2
            dirs = os.path.join(ds, 'leave/')
        if not os.path.isdir(dirs):
            os.makedirs(dirs)  # 判断目录是否存在，不存在则创建

        strs = base64Imag
        suffix = re.findall(r'/(\w+?);', strs[0])[0]  # 取得文件后缀
        # 拼接服务器上的文件名
        # datetime.now()取得当前时间，精确到了微秒，一般来说是唯一的了，因为目录是日期，所以文件名就去掉日期，最后会是一串数字
        img_name = str(work_id) + '_' + re.sub(r':|\.', '', datetime.now().__str__().split(' ')[1]) + '.' + suffix
        img_path = os.path.join(dirs, img_name)
        with open(img_path, 'wb') as out:
            out.write(base64.b64decode(strs[1]))  # base64解码，再写入文件
            out.flush()
            urls = os.path.join(WEB_HOST_MEDIA_URL, dir_name, response['arri_OR_leav'] + "/", img_name)  # '[/--sp--/]'   拼接URL，URL与URL之间用[/--sp--/]隔开
        # result['status'] = status.HTTP_200_OK
        # result['message'] = '图片上传成功'
        result['urls'] = urls  # urls[:len(urls) - len('[/--sp--/]')]   去掉末尾的[/--sp--/]

        # 外键查询组别的id
        # d = Department.objects.filter(dep_name=response['group']).first()
        # 匹配到对象的 比较特殊 必须使用 模型类的 实例，而不是具体的参数值
        a = UserProfile.objects.get(workid=work_id)
        # 找到workid然后把照片放进去
        new_img = CheckinTable.objects.filter(workid=a, date_today=date.today().__str__())
        if tag == 1:
            new_img.update(
                arr_time=response['arr_time'],
                arr_photo=urls,  # 拿到图片
                supp_status=response['supp'],
                tags=tag
            )
        if tag == 2 or tag == 3:
            new_img.update(
                lea_time=response['arr_time'],
                lea_photo=urls,  # 拿到图片
                supp_status=response['supp'],
                tags=tag
            )

        if new_img:
            result["data"].append("Success")
            result["msg"] = "Picture is successfully stocked ! "
        else:
            result['code'] = 400,
            result["data"].append("This is not successfully stocked")
            result["msg"] = "This is not successfully stocked"

    return JsonResponse(result)

    # return HttpResponse('上传成功！')

    # return render(request, 'employeur/aaa.html')


# # 搜索框的匹配
@csrf_exempt
@authentication_classes([JwtHeaderParamsAuthentication, ])
def searchBar(request):
    result = {
        "version": "1.0",
        "code": 200,
        "status": '',
        "data": [],
        "message": "Success!"
    }
    group = request.GET.get('group')
    tab = request.GET.get('tab')
    search_time = request.GET.get('search_time')
    print(group)
    print(tab)
    print(search_time)

    return JsonResponse(result)


class UsersModelForm(forms.ModelForm):
    class Meta:
        model = models.AccountLogin
        fields = ['account_num', 'account_password', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name == "account_password":
                continue
            field.widget.attrs = {"class": "input-content"}


@require_http_methods(['POST'])
def add_users(request):
    response = {}
    try:
        if request.method == 'GET':
            aa = request.GET.get('a')
            employee = models.AccountLogin.objects.get(id=aa)
            response['msg'] = 'success'
            response['error_num'] = 0
        else:
            aa = request.POST.get('a')
            pp = request.POST.get('p')
            # content = request.POST.get('content')
            # price = request.POST.get('price')
            # book = AccountLogin(account_num=request.GET.get('account_num'))
            # book.save()
            # AccountLogin.objects.create()
            response['result'] = pp
            response['msg'] = 'success'
            response['error_num'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1

    return JsonResponse(response)


def register(request):
    if request.method == 'POST':
        account_num = request.POST['user.account']
        account_password = request.POST['user.password']
        models.AccountLogin.objects.create(account_num=account_num, employ_name=account_password)
        return render(request, 'employeur/index.html')


def user_edit(request, nid):
    row_object = models.AccountLogin.objects.filter(id=nid).first()

    if request.method == 'GET':
        form = UsersModelForm(instance=row_object)
        return render(request, 'employeur/user_edit.html', {'form': form})

    form = UsersModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/user/list')
    return render(request, 'employeur/user_edit.html', {'form': form})

# 校验失败 显示提示信息


def user_list(request):
    form = UsersModelForm()
    if request.method == 'GET':
        # testf = models.Employee.objects.all()
        return render(request, 'employeur/user_list.html', {'form': form})


def user_delete(request, nid):
    models.AccountLogin.objects.filter(id=nid).delete()
    return redirect('employeur/user_list.html')


def index(request):
    user_list = models.Employee.objects.all()
    return render(request, 'employeur/index.html', {'user_list':  user_list})

# 信息新增处理函数


def add(request):
    if request.method == 'GET':
        return render(request, 'employeur/add.html')
    else:
        e_no = request.POST['e_no']
        e_name = request.POST['e_name']
        models.Employee.objects.create(employ_no=e_no, employ_name=e_name)
    return redirect('../')

#
# def get_check(request):
#     if request.method == 'GET':
#         return render(request, 'employeur/index.html')

# 员工上班打卡


def check_i(request):

    if request.method == 'GET':
        e_id = request.GET["id"]
        employee = models.Employee.objects.get(id=e_id)
        return render(request, 'employeur/check_i.html', {'Employee': employee})

    else:
        etime = time.strftime("%H:%M:%S", time.localtime())
        e_id = request.POST["id"]
        models.Employee.objects.filter(id=e_id).update(employ_time_in=etime)

        return redirect('../')

# 员工下班打卡


def check_o(request):
    if request.method == 'GET':

        e_id = request.GET["id"]
        employee = models.Employee.objects.get(id=e_id)
        return render(request, 'employeur/check_o.html', {'Employee': employee})

    else:
        etime = time.strftime("%H:%M:%S", time.localtime())
        e_id = request.POST["id"]
        models.Employee.objects.filter(id=e_id).update(employ_time_out=etime)

        return redirect('../')

# 信息修改处理函数


def edit(request):
    if request.method == 'GET':
        id = request.GET.get("id")
        conn = pymysql.connect(host="localhost", user="root", passwd="root", db="egs", charset='utf8')
        conn = conn.cursor()
        conn.execute("SELECT id, employ_no, employ_name, check_time, check_out FROM msm_employee where id =%s", [id])
        employee = conn.fetchone()
        return render(request, 'employeur/edit.html', {'Employee': employee})
    else:
        id = request.POST.get("id")
        # student_no = request.POST.get('student_no', '')
        # student_name = request.POST.get('student_name', '')
        conn = pymysql.connect(host="localhost", user="root", passwd="root ", db="egs", charset='utf8')
        conn = conn.cursor()
        e_time = time.strftime("%H:%M:%S", time.localtime())
        conn.execute("UPDATE msm_employee set check_out=%s where id =%s", [e_time, id])
        conn.commit()
        return redirect('../')


# 信息删除处理函数
# def delete(request):
#     id = request.GET.get("id")
#     conn = pymysql.connect(host="localhost", user="root", passwd="123456", db="egs", charset='utf8')
#     with conn.cursor(cursorclass=pymysql.cursors.DictCursor) as cursor:
#         cursor.execute("DELETE FROM test_connect WHERE id =%s", [id])
#     conn.commit()
#     return redirect('../')

def login01(request):
    if request.method == 'GET':
        print("GET####################")
        form = UsersModelForm()
        return render(request, 'employeur/login_page.html', {'form': form})
    else:
        print("POST####################")
        form = UsersModelForm(data=request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            return HttpResponse("提交成功")
        # models.Employee.objects.create(employ_no=e_no, employ_name=e_name)
    return render(request, 'employeur/login_page.html', {'form': form})
    # return redirect('../api/')

#
# def get_check(request):
#     if request.method == 'GET':
#         return render(request, 'employeur/index.html')

# 员工上班打卡
