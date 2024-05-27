from django.contrib import admin
from userauths.models import User,Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display=['full_name','user','date']



admin.site.register(User)
admin.site.register(Profile,ProfileAdmin)

