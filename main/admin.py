from django.contrib import admin
from .models import ProgramInfo, User

# Register your models here.


@admin.register(ProgramInfo)
class BankAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'version',
        'dep',
        'start_app',
        'hash',
        'type',
        'program'
    ]


    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['hash', 'dep']
        else:
            return ['hash']


@admin.register(User)
class BankAdmin(admin.ModelAdmin):
    list_display = [
        'username'
    ]