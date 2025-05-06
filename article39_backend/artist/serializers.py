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
        read_only_fields = [
            "id",
            "status",
            "completed_at",
            "user",
            "created_at",
            "amount",
        ]        


class PaymentToGetSerializer(serializers.ModelSerializer):
    gig_name = serializers.CharField(source="gig.title", read_only=True)
    min_payment = serializers.DecimalField(
        source="gig.min_payment", max_digits=10, decimal_places=2, read_only=True
    )
    max_payment = serializers.DecimalField(
        source="gig.max_payment", max_digits=10, decimal_places=2, read_only=True
    )
    song_name = serializers.CharField(source="song.title", read_only=True)
    payment_status = serializers.SerializerMethodField()

    class Meta:
        model = GigApplication
        fields = ["id", "status", "applied_at", "gig_name", "song_name", "min_payment", "max_payment", "payment_status"]

    def get_payment_status(self, obj):
        payment = getattr(obj, "payment_gig_application", None)
        return payment.status if payment else "NOT_REQUESTED"


class DocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = "__all__"
        read_only_fields = ["id", "updated_at", "artist"]
