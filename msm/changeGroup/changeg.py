
from datetime import date
from django.http import JsonResponse
import json
from rest_framework.views import APIView
from msm.models import Department
from msm.models import UserProfile
from msm.models import ChangeGroup
from msm.extentions.auth import JwtHeaderParamsAuthentication


class Groupechange(APIView):
    authentication_classes = [JwtHeaderParamsAuthentication, ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = {
            "version": "1.0",
            "code": 200,
            "data": [],
            "message": "Success!"
        }

    def get(self, request):
        print("$$$$$$$$$$$$$$$$$$$")
        uinfo = request.user
        role = uinfo.get("groups")
        print(uinfo)
        if role == "all":
            cg = ChangeGroup.objects.filter(date_today=date.today().__str__(), data_status=1)
            # 中间部门
        elif "," in role:
            group_set = role.split(',')
            gg = []
            for g in range(len(group_set)):
                gg.append(group_set[g])
            group_id_list = Department.objects.filter(dep_name__in=gg)
            cg = ChangeGroup.objects.filter(date_today=date.today().__str__(), start_group__in=group_id_list, data_status=1)
        else:
            group_id_list = Department.objects.filter(dep_name=role)
            cg = ChangeGroup.objects.filter(date_today=date.today().__str__(), start_group__in=group_id_list, data_status=1)
        for c in cg:
            g = {
                "workid": c.cg_workid_id,
                "fasname": str(c.cg_workid),
                "starttime": c.start_time,
                "endtime": c.finish_time,
                "from_group": c.start_group.dep_name + "-" + c.start_group.mission,
                "to_group": c.finish_group.dep_name + "-" + c.finish_group.mission,
            }
            self.result["data"].append(g)

        return JsonResponse(self.result)

    def post(self, request):
        res = json.loads(request.body)
        # print(res)
        # print(type(res['from_group']))
        # 一开始提交换组数据
        if res['endtime'] == 'NO':
            if type(res['from_group']) is list:
                gid1 = Department.objects.get(dep_name=res['from_group'][0], mission=res['from_group'][1])
            else:
                gid1 = Department.objects.get(mission=res['from_group'])
            gid2 = Department.objects.get(dep_name=res['to_group'][0], mission=res['to_group'][1])
            # 提交的是名字
            if res['flag'] == "name":
                user = UserProfile.objects.filter(first_name=res['name'].split(' ')[0],
                                                  second_name=res['name'].split(' ')[1]).first()
            # 提交的是工号
            else:
                user = UserProfile.objects.filter(workid=res['name']).first()
            if user:
                c = ChangeGroup(start_time=res['time'],
                                start_group=gid1,
                                finish_group=gid2,
                                cg_workid=user)
                c.save()
                self.result["message"] = "Ok !!"
            else:
                self.result["code"] = 999
                self.result["message"] = "Workid is not right, please try again !!"
        # 回来签回来的时间
        else:
            c = ChangeGroup.objects.filter(cg_workid_id=res['name'], start_time=res['time'])
            if c:
                c.update(finish_time=res['endtime'])
                self.result["message"] = "Update !!"
            else:
                self.result["code"] = 999
                self.result["message"] = "Workid is not right, please try again !!"

        return JsonResponse(self.result)