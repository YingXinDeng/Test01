from django.urls import path, include, re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from msm.divi.account import Authoaccount
from rbac.views import ExistUser, checkname, MenuData, DepsApis, CheckinList
from msm.changeGroup.changeg import Groupechange

urlpatterns = [
    # path('', include(router.urls)),
    path('', views.index),
    # stock picture info
    path('updateinfo/', views.updateinfo),
    re_path(r'^updateinfo/$', views.updateinfo),
    # for searching by group in changegroup center
    re_path(r'^change/group/$', Groupechange.as_view()),
    # get department info list   views.DepsApis.as_view()
    path('department/', DepsApis.as_view()),
    path('cinfo/', CheckinList.as_view()),
    # get department name by department id
    # re_path('department/(?P<d_id>\d+)/', views.DepsApis.as_view()),
    # add employee information
    re_path(r'^addeinfo/$', views.AddEmployeeInfo),
    # show all employee info list
    path('employeeinfo/', views.EmployeeInfo.as_view()),
    re_path(r'^employeeinfo/$', views.EmployeeInfo.as_view()),
    # 通过组名获取员工签到列表
    re_path('checkin/(?P<group_mission>.*)/', views.CheckinInfo.as_view()),
    # 获取签完名的照片的数据
    # re_path('checkin/data/', views.EmployeeInfo.as_view()),
    # 获取菜单的数据
    re_path(r'menu/data/$', MenuData.as_view()),
    # 搜索条的请求数据
    re_path('search/data/(?P<se_name>\D+)', views.searchBar),
    # 搜索签到和换组的数据
    re_path(r'^signature/changegroup/list/$', views.CheckIn.as_view()),
    # 加班表单提交
    re_path(r'^overwork/$', views.overwork),
    # 图表
    re_path(r'^analyse/$', views.chartView.as_view()),
    #  登录
    re_path(r'^user/login/$', views.Users.login_user),
    re_path('user/logout/', views.Users.logout_user),
    re_path(r'^pro/test/$', views.Autho.as_view()),
    re_path(r'^pro/order/$', views.ProOrder.as_view()),
    re_path(r'^login/$', Authoaccount.as_view()),
    re_path(r'UserExist/$', ExistUser.as_view()),
    re_path(r'^checkname/$', checkname),
    # 获取公司列表的
    re_path(r'^company/$', views.companydata),
 ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



