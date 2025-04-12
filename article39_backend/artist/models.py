from django.db.models.signals import post_save
from django.dispatch import receiver
from utils import send_song_status_update
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

    def __str__(self):
        return self.artist.username


# gigs -> users can apply for gigs
# admin -> approve/reject gigs
class GigApplication(models.Model):
    user = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name="application_user"
    )
    gig = models.ForeignKey(
        "administrator.Gig", on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("PENDING", "Pending"),
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected"),
        ],
        default="PENDING",
    )
    song = models.ForeignKey(
        "artist.Song",
        on_delete=models.CASCADE,
        related_name="song_id",
        null=True,
        blank=True,
    )
    applied_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name="payment_user"
    )
    gig = models.ForeignKey(
        "administrator.Gig", on_delete=models.CASCADE, related_name="payment_gig"
    )
    STATUS = (
        ("DUE", "Due"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("REJECTED", "Rejected"),
    )
    status = models.CharField(max_length=50, choices=STATUS, default="DUE")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    PAYMENT_METHOD = (
        ("MOBILE", "Mobile"),
        ("BANK", "Bank"),
    )
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD)

    # for mobile payment
    MOBILE_PAYMENT_METHOD = (
        ("bKash", "bKash"),
        ("Nagad", "Nagad"),
        ("Rocket", "Rocket"),
        ("DBBL", "DBBL"),
    )
    mobile_payment_method = models.CharField(
        max_length=50, choices=MOBILE_PAYMENT_METHOD, blank=True, null=True
    )
    mobile_number = models.CharField(max_length=50, blank=True, null=True)

    # for bank payment
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)


class Song(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="songs",
    )
    title = models.CharField(max_length=255)
    audio_url = models.URLField()
    duration = models.IntegerField(blank=True, null=True)
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


# django signal on song status change
@receiver(post_save, sender=Song)
def song_status_change(sender, instance, created, **kwargs):
    if not created:
        # If the song status is changed
        if instance.status != "PENDING":
            # Send email to the artist
            send_song_status_update(
                song_title=instance.title,
                user_name=instance.artist.singer_musician_info.full_name_english,
                status=instance.status,
                email=instance.artist.artist.email,
            )
            print("email sent!")
