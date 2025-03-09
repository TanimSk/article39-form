from django.db import models
from django.contrib.postgres.fields import ArrayField
from uuid import uuid4

class Artist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    # Basic Information
    full_name_english = models.CharField(max_length=255)
    full_name_bengali = models.CharField(max_length=255, blank=True, null=True)
    stage_name = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Profile & Genre
    GENRE_CHOICES = [
        ('Rock', 'Rock'),
        ('Folk', 'Folk'),
        ('Pop', 'Pop'),
        ('Jazz', 'Jazz'),
        ('Classical', 'Classical'),
    ]
    primary_genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    secondary_genre = models.CharField(max_length=50, choices=GENRE_CHOICES, blank=True, null=True)
    performance_languages = ArrayField(models.CharField(max_length=50), blank=True, null=True)

    # Contact Details
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    # Social / Online Presence
    website = models.URLField(blank=True, null=True)
    social_links = ArrayField(models.URLField(), blank=True, null=True)  # Multiple social media links

    # Bio / Artist Statement
    bio = models.TextField(max_length=1000, blank=True, null=True)

    # Portfolio
    portfolio_description = models.TextField(blank=True, null=True)
    credits = models.CharField(max_length=255, blank=True, null=True)
    content_links = ArrayField(models.URLField(), blank=True, null=True)  # Multiple content links
    content_uploads = ArrayField(models.URLField(), blank=True, null=True)  # Now stores URLs instead of file uploads

    # Equipment & Technical Requirements
    instruments = ArrayField(models.CharField(max_length=255), blank=True, null=True)  # List of instruments
    technical_preferences = models.TextField(blank=True, null=True)

    # Availability / Commitment
    available_from_times = ArrayField(models.TimeField(), blank=True, null=True)
    available_to_times = ArrayField(models.TimeField(), blank=True, null=True)
    available_from_dates = ArrayField(models.DateField(), blank=True, null=True)
    available_to_dates = ArrayField(models.DateField(), blank=True, null=True)

    # Verification & Agreements
    government_id_upload = models.URLField(blank=True, null=True)  # Now stores URL instead of file upload
    consent_promotion = models.BooleanField(default=False)
    agree_terms = models.BooleanField(default=False)

    # Payment Preferences
    preferred_payment_method = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.full_name_english or self.stage_name
