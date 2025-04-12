from artist.models import Song, Artist, GigApplication, Payment
from rest_framework import serializers


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = "__all__"
        read_only_fields = ["id", "artist", "duration", "added_at", "status"]

class GigApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GigApplication
        fields = ["id", "user", "gig", "status", "applied_at"]
        read_only_fields = ["id", "user", "applied_at"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["id", "status", "completed_at", "user", "created_at"]