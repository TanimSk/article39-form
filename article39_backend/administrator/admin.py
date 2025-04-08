from django.contrib import admin
from administrator.models import Gig


@admin.register(Gig)
class GigAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "datetime")
