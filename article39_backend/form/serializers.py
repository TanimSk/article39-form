from rest_framework import serializers
from form.models import Artist

class ArtistSerializer(serializers.ModelSerializer):
    # Handling ArrayFields properly
    performance_languages = serializers.ListField(child=serializers.CharField(max_length=50), required=False)
    social_links = serializers.ListField(child=serializers.URLField(), required=False)
    content_links = serializers.ListField(child=serializers.URLField(), required=False)
    content_uploads = serializers.ListField(child=serializers.URLField(), required=False)  # Changed from FileField to URLField
    instruments = serializers.ListField(child=serializers.CharField(max_length=255), required=False)
    available_from_times = serializers.ListField(child=serializers.TimeField(), required=False)
    available_to_times = serializers.ListField(child=serializers.TimeField(), required=False)
    available_from_dates = serializers.ListField(child=serializers.DateField(), required=False)
    available_to_dates = serializers.ListField(child=serializers.DateField(), required=False)
    
    # Updating government_id_upload field
    government_id_upload = serializers.URLField(required=False, allow_null=True)  # Changed from FileField to URLField

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
