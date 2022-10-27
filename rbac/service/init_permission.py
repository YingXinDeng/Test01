from ..models import UserInfo, Menu
from django.conf import settings  # 通过这种方式导入配置，具有可迁移性


def init_permission(request, user_obj):
    """
    初始化用户权限, 写入session
    :param request:
    :param user_obj:
    :return:
    """

    request.session['is_login'] = True
    permission_queryset = user_obj.roles.filter(permissions__url__isnull=False).values('permissions__url',
                                                                                       'permissions__title',
                                                                                       'permissions__is_menu',
                                                                                       'permissions__menu_id'
                                                                                       ).distinct()

    # 用户权限url列表，--> 用于中间件验证用户权限
    permission_url_list = []
    # 用户权限url所属菜单列表 [{"title":xxx, "url":xxx, "menu_id": xxx},{},]
    menu_list = []
    # menu_id = 1
    for item in permission_queryset:
        permission_url_list.append(item['permissions__url'])

        if item['permissions__is_menu']:
            # menu_id += menu_id
            menu_list.append(item['permissions__menu_id'])

    # 注：session在存储时，会先对数据进行序列化，因此对于Queryset对象写入session，加list()转为可序列化对象
    # 保存用户权限url列表
    request.session[settings.SESSION_PERMISSION_URL_KEY] = permission_url_list
    # 给菜单排序 要不然乱糟糟
    menu_list = sorted(menu_list)
    request.session[settings.SESSION_PERMISSION_MENU_KEY] = menu_list
    print("这是这个用户的角色 : ", user_obj.nickname)
    request.session["user_info"] = {'id': user_obj.id, 'name': user_obj.username, "role": user_obj.nickname}
    # 保存 权限菜单 和所有 菜单；用户登录后作菜单展示用


