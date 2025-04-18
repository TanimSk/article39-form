from django.contrib import admin
from administrator.models import Gig, User


@admin.register(Gig)
class GigAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "datetime")

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "is_admin", "is_artist")    
    search_fields = ("username",)
