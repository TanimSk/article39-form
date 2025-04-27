from artist.models import Song, Artist, GigApplication, Payment, Documents
from rest_framework import serializers


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = "__all__"
        read_only_fields = [
            "id",
            "artist",
            "duration",
            "added_at",
            "status",
            "upload_status",
            "youtube_url",
            "youtube_like_count",
            "youtube_comment_count",
            "youtube_view_count",
        ]


class GigApplicationSerializer(serializers.ModelSerializer):
    song_music_details = SongSerializer(source="song", read_only=True)

    class Meta:
        model = GigApplication
        fields = ["user", "gig", "status", "applied_at", "song_music_details"]
        read_only_fields = ["id", "user", "applied_at"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["id", "status", "completed_at", "user", "created_at"]


class DocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = "__all__"
        read_only_fields = ["id", "updated_at", "artist"]
