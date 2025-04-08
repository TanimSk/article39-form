from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # Boolean fields to select the type of account.
    is_admin = models.BooleanField(default=False)
    is_artist = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Gig(models.Model):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    datetime = models.DateTimeField()


# gigs -> users can apply for gigs
# admin -> approve/reject gigs
class GigApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")], default="PENDING")
    applied_at = models.DateTimeField(auto_now_add=True)