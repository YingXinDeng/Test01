from django.contrib import admin
from rbac import models
# Register your models here.


class PermissionAdmin(admin.ModelAdmin):
    list_display = ["title", 'url']
    list_editable = ['url']


admin.site.register(models.Permission, PermissionAdmin)
admin.site.register(models.Role)
admin.site.register(models.UserInfo)
admin.site.register(models.Menu)