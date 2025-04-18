from django.contrib import admin
from artist.models import Artist, Song, GigApplication


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("artist", "is_verified")
    search_fields = ("artist__username",)
    list_filter = ("is_verified",)
    ordering = ("-artist__date_joined",)

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "artist", "duration", "status")
    search_fields = ("title", "artist__artist__username")
    list_filter = ("artist__is_verified",)
    ordering = ("-artist__artist__date_joined",)

@admin.register(GigApplication)
class GigApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "gig", "status", "applied_at")
    search_fields = ("user__username", "gig__title")
    list_filter = ("status",)
    ordering = ("-applied_at",)
