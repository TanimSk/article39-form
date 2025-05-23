from rest_framework import serializers
from form.models import Artist, FilmMaker

class ArtistSerializer(serializers.ModelSerializer):
    # Handling ArrayFields properly
    performance_languages = serializers.ListField(child=serializers.CharField(max_length=50), required=False)
    social_links = serializers.ListField(child=serializers.URLField(), required=False)
    content_links = serializers.ListField(child=serializers.URLField(), required=False)
    content_uploads = serializers.ListField(child=serializers.URLField(), required=False)  # Changed from FileField to URLField
    instruments = serializers.ListField(child=serializers.CharField(max_length=255), required=False)
    available_timelines = serializers.ListField(child=serializers.JSONField(), required=False)
    
    # Updating government_id_upload field
    government_id_upload = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Artist
        fields = '__all__'
    
    def validate_mobile_number(self, value):
        """Validate mobile number format"""
        if not value.startswith('+') or not value[1:].isdigit():
            raise serializers.ValidationError("Mobile number must start with '+' and contain only digits.")
        return value

    def validate(self, data):
        """Ensure at least one language is selected"""
        if 'performance_languages' in data and not data['performance_languages']:
            raise serializers.ValidationError("At least one performance language must be selected.")
        return data


class FilmMakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilmMaker
        fields = '__all__'

