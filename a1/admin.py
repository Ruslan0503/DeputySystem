from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Profile)
admin.site.register(models.OrganizeSession)
admin.site.register(models.SessionTopic)
admin.site.register(models.UserSession)
admin.site.register(models.Role)
admin.site.register(models.OkrugModel)