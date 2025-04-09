from django.db import models
from django.conf import settings
import uuid


class Artist(models.Model):
    artist = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="artist_profile",
    )
    singer_musician_info = models.OneToOneField(
        "form.Artist",
        on_delete=models.DO_NOTHING,
        related_name="artist_info",
        null=True,
        blank=True,
    )
    filmmaker_info = models.OneToOneField(
        "form.Filmmaker",
        on_delete=models.DO_NOTHING,
        related_name="filmmaker_info",
        null=True,
        blank=True,
    )
    is_verified = models.BooleanField(default=False)


class Song(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="songs",
    )
    title = models.CharField(max_length=255)
    song_url = models.URLField()
    duration = models.IntegerField()
    GENRE = (
        ("pop", "Pop"),
        ("rock", "Rock"),
        ("hip-hop", "Hip-Hop"),
        ("jazz", "Jazz"),
        ("metal", "Metal"),
        ("folk", "Folk"),
    )
    genre = models.CharField(max_length=50, choices=GENRE)
    STATUS = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )
    status = models.CharField(max_length=50, choices=STATUS, default="PENDING")
    added_at = models.DateTimeField(auto_now_add=True)
