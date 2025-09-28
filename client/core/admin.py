from django.contrib import admin
from task.models import User

#-------------------WorkspaceMember----------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
