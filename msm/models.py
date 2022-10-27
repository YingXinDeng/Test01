from django.db import models
import datetime
import django.utils.timezone as timezone
# Create your models here.
# from django.contrib.auth.models import AbstractUser


# 国家表 以及对应的仓库表


class Country(models.Model):
    count_name = models.CharField(max_length=20, unique=False)
    count_ware = models.CharField(max_length=32, unique=True, null=True)
    count_desc = models.CharField(max_length=32, null=True)

    def __str__(self):
        return "%s %s" % (self.count_name, self.count_ware)


# 部门表

class Department(models.Model ):
    warehouse = models.ForeignKey(to="Country", on_delete=models.DO_NOTHING, null=True, blank=True)
    dep_name = models.CharField(max_length=20, unique=False)
    mission = models.CharField(max_length=20, unique=True)
    mission_desc = models.CharField(max_length=32, null=True)

    def __str__(self):
        return "%s %s" % (self.mission, self.dep_name)


# 合同类型
class ContractType(models.Model):
    cont_name = models.CharField(max_length=20, unique=True)
    cont_desc = models.CharField(max_length=20, unique=True, blank=True)


# 公司类型
class CompanyType(models.Model):
    com_name = models.CharField(max_length=20, unique=True)
    com_desc = models.CharField(max_length=20, unique=True, blank=True)
    is_active = models.BooleanField(default=True, null=False, blank=True)


# 员工工号表

class UserAccount(models.Model):
    work_num = models.ForeignKey(max_length=50, verbose_name='WorkID', default='123456', to="UserProfile", to_field="workid", on_delete=models.DO_NOTHING, null=True, blank=True)
    account_num = models.ForeignKey(to="AccountLogin", on_delete=models.DO_NOTHING, default=1, null=True)
    account_status = models.SmallIntegerField(choices=((1, 'OK'), (2, 'BAD'), (0, 'unknown')), default=0, null=True, blank=True)


# 员工账号登录表

class AccountLogin(models.Model):
    account_num = models.CharField(max_length=30, verbose_name=u'Account_number', default=u'')
    account_password = models.CharField(max_length=20, verbose_name=u'Account_password', default=u'')
    account_status = models.SmallIntegerField(choices=((1, 'OK'), (2, 'BAD'), (0, 'unknown')), default=0, null=True,
                                              blank=True)


# 员工个人信息类，继承自AbstractBaseUser
class UserProfile(models.Model):

    workid = models.CharField(max_length=32, null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=50, null=False, verbose_name=u'First name', default=u'')
    second_name = models.CharField(max_length=50, null=False, verbose_name=u'Second name', default=u'')
    birthday = models.DateField(verbose_name=u'Birthday', null=True)
    gender = models.SmallIntegerField(choices=((1, 'male'), (2, 'female'), (0, 'unknown')), default=0, null=True, blank=True)
    address = models.CharField(max_length=100, default='', verbose_name="Address", null=True, blank=True)
    join_time = models.DateField(verbose_name="Join time", null=True)
    end_time = models.DateField(verbose_name="End time", null=True)
    mobile = models.CharField(verbose_name="Phone number", max_length=15, null=True, blank=True)
    type_choice = (
        (1, "CDI"),
        (2, "CDD"),
        (3, "Temporary"),
        (4, "Trial"),
    )
    # company = models.SmallIntegerField(choices=company_choice, default=0, null=True, blank=True)
    contract_type = models.SmallIntegerField(verbose_name="Level", choices=type_choice, default=3, null=True, blank=True)
    company = models.ForeignKey(to="CompanyType", on_delete=models.DO_NOTHING, null=True, blank=True)
    # contract_type = models.ForeignKey(to="ContractType", on_delete=models.DO_NOTHING, verbose_name="Level", null=True, blank=True)
    # group_name = models.ForeignKey(related_name="Department", to="Department",  on_delete=models.DO_NOTHING,  null=True)
    dep_mission = models.ForeignKey(related_name="Department_Mission", to="Department",  on_delete=models.DO_NOTHING, null=True)
    created = models.DateTimeField(verbose_name="Creat time", null=True, default=timezone.now)
    data_status = models.BooleanField(default=True, null=False, blank=False)

    class Meta:
        ordering = ['-join_time']

    # image = models.ImageField(upload_to="image/%Y/%m", default=u'image/default.png', max_length=100)
    def __str__(self):
        return "%s %s" % (self.first_name, self.second_name)

# 员工上下班打卡信息表


class CheckinTable(models.Model):
    workid = models.ForeignKey(max_length=50, verbose_name='WorkID', default='123456', to="UserProfile", to_field="workid", on_delete=models.DO_NOTHING, null=True, blank=True)
    group = models.ForeignKey(verbose_name="Depart", to="Department", on_delete=models.DO_NOTHING, default='Not defound', null=True, blank=True)
    # 早上自动新增的
    date_today = models.DateField(default=timezone.now, null=True, blank=True)
    # 用于标识有上班的还是下班的电子签名
    tags = models.SmallIntegerField(default=0, null=True, blank=True)
    arr_time = models.CharField(max_length=32, null=True, blank=True)
    lea_time = models.CharField(max_length=32, null=True, blank=True)
    arr_photo = models.ImageField(upload_to='photos', default='', verbose_name='签到', blank=True, null=True)
    lea_photo = models.ImageField(upload_to='photos', default='', verbose_name='离开', blank=True, null=True)
    supp_status = models.SmallIntegerField(choices=((1, 'arrive'), (2, 'leave'), (0, 'No')), default=0, null=True, blank=True)
    data_status = models.BooleanField(default=True, null=True, blank=True)

    # 按照序号顺序排列

    class Meta:
        ordering = ['arr_time']


class SubMenu(models.Model):

    # 父菜单的名字或者id
    fathermenu = models.CharField(max_length=32, null=True, blank=True)
    menuid = models.CharField(max_length=32, null=True, blank=True)
    # 子菜单的名字  也是组名
    title_group = models.ForeignKey(to="Department", on_delete=models.DO_NOTHING, default=1, null=True)
    router = models.CharField(max_length=32, null=True, blank=True)
    menu_status = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        ordering = ['menuid']

    def __str__(self):
        return self.title_group


class ChangeGroup(models.Model):
    # 开始和结束换组的时间
    start_time = models.CharField(max_length=32, null=True, blank=True)
    finish_time = models.CharField(max_length=32, null=True, blank=True)
    # 原组 换到的组
    start_group = models.ForeignKey(to="Department", related_name="begin_group", on_delete=models.DO_NOTHING, default=1, null=True)
    finish_group = models.ForeignKey(to="Department", related_name="end_group", on_delete=models.DO_NOTHING, default=2, null=True)
    cg_workid = models.ForeignKey(max_length=50, verbose_name='WorkID', default='123456', to="UserProfile", to_field="workid", on_delete=models.DO_NOTHING, null=True, blank=True)
    # 换组状态 0 是开始了换组，1是换组结束
    change_status = models.BooleanField(default=True, null=True, blank=True)
    # 记录当日 日期
    date_today = models.DateField(default=datetime.date.today(), null=True, blank=True)
    # 突然删除了会被标记这条信息不可用
    data_status = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        ordering = ['change_status']

    def __str__(self):
        return "%s %s" % (self.cg_workid, self.start_time)


class ExternalWork(models.Model):
    # 员工ID
    ew_workid = models.ForeignKey(max_length=50, verbose_name='WorkID', default='123456', to="UserProfile", to_field="workid", on_delete=models.DO_NOTHING, null=True, blank=True)
    ew_name = models.CharField(max_length=50, null=True, blank=True)
    ex_group = models.ForeignKey(to="Department", related_name="group", on_delete=models.DO_NOTHING, default=1, null=True)
    # 加班时长  开始 结束
    ex_start_time = models.CharField(max_length=50, null=True, blank=True)
    ex_end_time = models.CharField(max_length=50, null=True, blank=True)
    ex_long_time = models.DecimalField(default=0, max_digits=5, decimal_places=2)  # 3位整数，2位小数
    # 加班原因
    ex_work_reason = models.CharField(max_length=100, null=True, blank=True)
    # 加班日期N
    ex_work_date = models.DateField(default=datetime.date.today(), null=True, blank=True)
    # 加班奖励方式
    ex_work_way = models.CharField(max_length=32, null=True, blank=True)
    # 当有人的信息被删除的时候这个状态会标记为不激活
    ex_data_status = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        ordering = ['ex_long_time']
