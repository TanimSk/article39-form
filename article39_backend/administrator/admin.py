from django.contrib import admin
from administrator.models import Gig


@admin.register(Gig)
class GigAdmin(admin.ModelAdmin):
    list_display = ("artist", "gig_name", "gig_date", "status")
    list_filter = ("artist", "status")
    search_fields = ("artist__artist__username", "gig_name")
    ordering = ("-gig_date",)
    date_hierarchy = "gig_date"
    list_per_page = 10
