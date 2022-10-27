from django.db import models


class Menu(models.Model):
    """
    菜单
    """
    title = models.CharField(max_length=32, unique=True)
    router = models.CharField(default="homepage", max_length=32, unique=False)
    # 权重指数 用来进行排序
    weight = models.SmallIntegerField(default=0, null=True, blank=True)
    icon = models.CharField(max_length=32, unique=False, blank=True)
    parent = models.ForeignKey("Menu", null=True, blank=True, on_delete=models.DO_NOTHING)
    # 定义菜单间的自引用关系
    # 权限url 在 菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段（parent_id）
    # blank=True 意味着在后台管理中填写可以为空，根菜单没有父级菜单

    class Meta:
        ordering = ['weight']

    def __str__(self):
        # 显示层级菜单
        title_list = [self.title]
        p = self.parent
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '-'.join(title_list)


class Permission(models.Model):
    """
    权限
    """
    title = models.CharField(max_length=32, unique=True)
    url = models.CharField(max_length=128, unique=True)
    # 指示这个URL属于哪一个菜单的  去掉null为true在左连接的时候就不会全连接
    menu = models.ForeignKey("Menu", blank=True, on_delete=models.DO_NOTHING)
    is_menu = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        # 显示带菜单前缀的权限
        return '{menu}---{permission}'.format(menu=self.menu, permission=self.title)


class Role(models.Model):
    """
    角色：绑定权限
    """
    title = models.CharField(max_length=32, unique=True)
    permissions = models.ManyToManyField("Permission")
    # 定义角色和权限的多对多关系

    def __str__(self):
        return self.title


class UserInfo(models.Model):
    """
    用户：划分角色
    """
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    # 这个描述这个人的唯一权限
    nickname = models.CharField(max_length=32)
    roles = models.ManyToManyField("Role")
    # 定义用户和角色的多对多关系

    def __str__(self):
        return self.username
