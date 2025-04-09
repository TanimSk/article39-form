from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField
from uuid import uuid4
from datetime import datetime
from form.validator import validate_budget_breakdown


# Singer and Musician
class Artist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    # Basic Information
    full_name_english = models.CharField(max_length=255, blank=True, null=True)
    full_name_bengali = models.CharField(max_length=255, blank=True, null=True)
    stage_name = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Profile & Genre
    GENRE_CHOICES = [
        ("Rock", "Rock"),
        ("Folk", "Folk"),
        ("Pop", "Pop"),
        ("Jazz", "Jazz"),
        ("Classical", "Classical"),
        ("Hip-Hop", "Hip-Hop"),
    ]
    primary_genre = models.CharField(
        max_length=50, choices=GENRE_CHOICES, blank=True, null=True
    )
    secondary_genre = models.CharField(
        max_length=50, choices=GENRE_CHOICES, blank=True, null=True
    )
    performance_languages = ArrayField(
        models.CharField(max_length=50), blank=True, null=True
    )

    # Contact Details
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # Social / Online Presence
    website = models.URLField(blank=True, null=True)
    social_links = ArrayField(
        models.URLField(), blank=True, null=True
    )  # Multiple social media links

    # Bio / Artist Statement
    bio = models.TextField(max_length=1000, blank=True, null=True)

    # Portfolio
    portfolio_description = models.TextField(blank=True, null=True)
    credits = models.CharField(max_length=255, blank=True, null=True)
    content_links = ArrayField(
        models.URLField(), blank=True, null=True
    )  # Multiple content links
    content_uploads = ArrayField(
        models.URLField(), blank=True, null=True
    )  # Now stores URLs instead of file uploads

    # Equipment & Technical Requirements
    instruments = ArrayField(
        models.CharField(max_length=255), blank=True, null=True
    )  # List of instruments
    technical_preferences = models.TextField(blank=True, null=True)

    # Availability / Commitment
    # [{
    #   time: {
    #     from: "10:00AM",
    #     to: "12:00PM",
    #   },
    #   date: {
    #     from: "20-03-2025",
    #     to: "30-03-2025",
    #   },
    # },
    #  ....]
    available_timelines = ArrayField(JSONField(), blank=True, null=True)

    # Verification & Agreements
    government_id_upload = models.URLField(
        blank=True, null=True
    )  # Now stores URL instead of file upload
    consent_promotion = models.BooleanField(default=False, blank=True, null=True)
    agree_terms = models.BooleanField(default=False, blank=True, null=True)

    # Payment Preferences
    preferred_payment_method = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.email == "":
            self.email = None  # Convert empty string to NULL
        super().save(*args, **kwargs)


class FilmMaker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    basic_info = models.JSONField()
    project_info = models.JSONField()
    primary_contact_info = models.JSONField()
    brief_synopsis = models.TextField(null=True, blank=True)
    production_overview = models.JSONField()
    budget_breakdown = models.JSONField()
    payment_terms = models.JSONField()
    additional_details = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        self.validate_basic_info()
        self.validate_project_info()
        self.validate_primary_contact_info()
        self.validate_production_overview()
        self.validate_budget_breakdown()
        self.validate_payment_terms()
        self.validate_additional_details()

    def validate_basic_info(self):
        required_keys = [
            "full_name_en",
            "full_name_bn",
            "dob",
            "gender",
            "email",
            "phone",
            "address",
            "district",
            "post_office",
            "postal_code",
        ]

        if self.basic_info:
            for key in required_keys:
                if key not in self.basic_info:
                    raise ValidationError(f"Missing '{key}' in basic_info.")

            # must have an email, which is unique and valid
            email = self.basic_info.get("email")            
            if email:
                if not isinstance(email, str) or "@" not in email:
                    raise ValidationError(
                        "The 'email' field must be a valid email address."
                    )
                if FilmMaker.objects.filter(basic_info__email=email).exists():
                    raise ValidationError("The 'email' field must be unique.")
            else:
                raise ValidationError("The 'email' field is required.")

            dob = self.basic_info.get("dob")
            if dob:
                try:
                    datetime.strptime(dob, "%Y-%m-%d")
                except ValueError:
                    raise ValidationError(
                        "The 'dob' field must be a valid date in YYYY-MM-DD format."
                    )

    def validate_project_info(self):
        if self.project_info:
            if not all(
                key in self.project_info for key in ["project_title", "company_name"]
            ):
                raise ValidationError(
                    "Project info must include 'project_title' and 'company_name'."
                )

    def validate_primary_contact_info(self):
        if self.primary_contact_info:
            if not all(
                key in self.primary_contact_info
                for key in ["contact_name", "email", "phone"]
            ):
                raise ValidationError(
                    "Primary contact info must include 'contact_name', 'email', and 'phone'."
                )

    def validate_production_overview(self):
        if self.production_overview:
            if not all(
                key in self.production_overview
                for key in ["genre", "est_runtime", "expected_shoot_days"]
            ):
                raise ValidationError(
                    "Production overview must include 'genre', 'est_runtime', and 'expected_shoot_days'."
                )
            if "locations" in self.production_overview:
                if not all(
                    isinstance(loc, dict) and "type" in loc and "location" in loc
                    for loc in self.production_overview["locations"]
                ):
                    raise ValidationError(
                        "Each location in production overview must be a dictionary with 'type' and 'location'."
                    )

    def validate_budget_breakdown(self):
        if self.budget_breakdown:
            try:
                validate_budget_breakdown(self.budget_breakdown)
            except ValidationError as e:
                raise ValidationError(f"Budget Breakdown Error: {e}")

    def validate_payment_terms(self):
        if self.payment_terms:
            if (
                "total_budget" not in self.payment_terms
                or "payment_schedule" not in self.payment_terms
            ):
                raise ValidationError(
                    "Payment terms must include 'total_budget' and 'payment_schedule'."
                )

    def validate_additional_details(self):
        if self.additional_details:
            if (
                "note" not in self.additional_details
                or "attachments" not in self.additional_details
            ):
                raise ValidationError(
                    "Additional details must include 'note' and 'attachments'."
                )
            if not isinstance(self.additional_details.get("attachments"), list):
                raise ValidationError("Attachments must be a list.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
