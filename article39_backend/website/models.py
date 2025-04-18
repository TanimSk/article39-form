from django.db import models
from uuid import uuid4
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from datetime import datetime

# Image Courasel
class CouraselImages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    image = models.TextField(max_length=1000, blank=False, null=False)
    selected = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.image
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Courasel Images'
        verbose_name_plural = 'Courasel Images'


#Stories / Articles
class Stories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=1000, blank=False, null=False)
    cover_image = models.TextField(max_length=1000, blank=True, null=True)
    author = models.TextField(max_length=255, blank=False, null=False)
    content = models.TextField(max_length=100000, blank=False, null=False)
    tags = ArrayField(models.CharField(max_length=255), blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stories'
        verbose_name_plural = 'Stories'


#Events
class Events(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=1000, blank=False, null=False)
    cover_image = models.TextField(max_length=1000, blank=True, null=True)
    description = models.TextField(max_length=100000, blank=False, null=False)
    ticket_price = models.FloatField(blank=False, null=False)
    date = models.TextField(max_length=1000, blank=False, null=False)
    location = models.TextField(max_length=1000, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Events'
        verbose_name_plural = 'Events'

# Ticket Bookings
class TicketBookings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    buyer_name = models.TextField(max_length=1000, blank=False, null=False)
    buyer_email = models.EmailField(max_length=1000, blank=False, null=False)
    buyer_phone = models.TextField(max_length=1000, blank=False, null=False)
    number_of_tickets = models.IntegerField(blank=False, null=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.event.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ticket Bookings'
        verbose_name_plural = 'Ticket Bookings'


# Exhibitions
class Exhibitions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=1000, blank=False, null=False)
    cover_image = models.TextField(max_length=1000, blank=True, null=True)
    description = models.TextField(max_length=100000, blank=False, null=False)
    date = models.TextField(max_length=1000, blank=False, null=False)
    from_time = models.TextField(max_length=1000, blank=False, null=False)
    to_time = models.TextField(max_length=1000, blank=False, null=False)
    location = models.TextField(max_length=1000, blank=False, null=False)
    tags = ArrayField(models.CharField(max_length=255), blank=False, null=False)
    author = models.TextField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Exhibitions'
        verbose_name_plural = 'Exhibitions'


# Albums
class Albums(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=1000, blank=False, null=False)
    cover_image = models.TextField(max_length=1000, blank=True, null=True)
    description = models.TextField(max_length=100000, blank=False, null=False)
    genre = ArrayField(models.CharField(max_length=255), blank=False, null=False)
    category = ArrayField(models.CharField(max_length=255), blank=False, null=False)
    artist = ArrayField(models.CharField(max_length=255), blank=False, null=False)
    number_of_songs = models.IntegerField(blank=False, null=False)
    author = models.TextField(max_length=255, blank=False, null=False)
    tags = ArrayField(models.CharField(max_length=255), blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Albums'
        verbose_name_plural = 'Albums'


#Singles
class Singles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=1000, blank=False, null=False)
    cover_image = models.TextField(max_length=1000, blank=True, null=True)
    description = models.TextField(max_length=100000, blank=False, null=False)
    genre = ArrayField(models.CharField(max_length=255), blank=False, null=False)
    category = ArrayField(models.CharField(max_length=255), blank=False, null=False)
    artist = models.CharField(max_length=255, blank=False, null=False)
    number_of_songs = models.IntegerField(blank=False, null=False)
    author = models.TextField(max_length=255, blank=False, null=False)
    tags = ArrayField(models.CharField(max_length=255), blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Singles'
        verbose_name_plural = 'Singles'

# Shows
class Shows(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=1000, blank=False, null=False)
    cover_image = models.TextField(max_length=1000, blank=True, null=True)
    video_url = models.TextField(max_length=1000, blank=True, null=True)
    location = models.TextField(max_length=1000, blank=False, null=False)
    time = models.TextField(max_length=255, blank=False, null=False)
    date = models.TextField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Shows'
        verbose_name_plural = 'Shows'


def validate_show_bookings_date_range(value):
    # Check that the value is a list
    if not isinstance(value, list):
        raise ValidationError('Value must be a list.')
    
    for item in value:
        # Each item should be a dictionary with start_date and end_date
        if not isinstance(item, dict):
            raise ValidationError('Each item must be a dictionary.')
        
        start_date = item.get('start_date')
        end_date = item.get('end_date')
        
        # Ensure start_date and end_date are provided and are valid dates
        if not start_date or not end_date:
            raise ValidationError('Each item must have both start_date and end_date.')
        
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            if start_dt >= end_dt:
                raise ValidationError('start_date must be before end_date.')
        except ValueError:
            raise ValidationError('Invalid date format. Use YYYY-MM-DD.')


class ShowBookingInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    full_name = models.TextField(max_length=1000, blank=False, null=False)
    email = models.EmailField(max_length=1000, blank=False, null=False)
    phone = models.TextField(max_length=1000, blank=False, null=False)
    dates = models.JSONField(validators=[validate_show_bookings_date_range], default=list, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Show Booking Information'
        verbose_name_plural = 'Show Booking Information'
