from artist.models import Song, Artist
from rest_framework import serializers


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ["id", "title", "artist", "genre", "release_date", "duration"]
        read_only_fields = ["id", "artist"]
