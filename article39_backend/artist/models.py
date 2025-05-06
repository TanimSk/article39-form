from django.db.models.signals import post_save

# from django.dispatch import receiver
# from utils import send_song_status_update
from django.db import models
from django.conf import settings
import uuid
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError


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
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
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
    gig_application = models.OneToOneField(
        GigApplication,
        on_delete=models.CASCADE,
        related_name="payment_gig_application",
        blank=True,
        null=True,
    )
    STATUS = (
        ("DUE", "Due"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("REJECTED", "Rejected"),
    )
    status = models.CharField(max_length=50, choices=STATUS, default="DUE")

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

    # To be set by the admin
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    document_url = models.URLField(blank=True, null=True)


class Song(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="songs",
    )
    title = models.CharField(max_length=255)
    audio_url = models.URLField()
    thumbnail_url = models.URLField()

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

    # song upload status
    UPLOAD_STATUS = (
        ("NOT_UPLOADED", "Not Uploaded"),
        ("PROCESSING", "Processing"),
        ("UPLOADING", "Uploading"),
        ("UPLOADED", "Uploaded"),
    )
    upload_status = models.CharField(
        max_length=50, choices=UPLOAD_STATUS, default="NOT_UPLOADED"
    )
    youtube_url = models.URLField(blank=True, null=True)
    youtube_video_id = models.CharField(max_length=255, blank=True, null=True)
    youtube_like_count = models.IntegerField(blank=True, null=True)
    youtube_comment_count = models.IntegerField(blank=True, null=True)
    youtube_view_count = models.IntegerField(blank=True, null=True)

    status = models.CharField(max_length=50, choices=STATUS, default="PENDING")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_audio_duration(self, duration):
        self.duration = duration
        self.save(update_fields=["duration"])


def validate_document(item):
    if not isinstance(item, dict):
        raise ValidationError("Each item must be a JSON object.")
    if "document_type" not in item or "document_url" not in item:
        raise ValidationError(
            "Each item must contain 'document_type' and 'document_url'."
        )
    if not isinstance(item["document_type"], str):
        raise ValidationError("'document_type' must be a string.")
    if not isinstance(item["document_url"], str):
        raise ValidationError("'document_url' must be a string.")


class Documents(models.Model):
    artist = models.OneToOneField(
        Artist,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    documents = ArrayField(
        base_field=models.JSONField(validators=[validate_document]),
        blank=True,
        default=list,
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.artist.artist.username}"
