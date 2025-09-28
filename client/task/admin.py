from django.contrib import admin
from task.models import Task

#-------------------WorkspaceMember----------------------------
@admin.register(Task)
class UserAdmin(admin.ModelAdmin):
    pass
