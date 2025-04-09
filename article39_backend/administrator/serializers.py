from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from administrator.models import Gig


class CustomPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate(self, data):
        # Check if the new passwords match
        if data["new_password1"] != data["new_password2"]:
            raise serializers.ValidationError("The two new passwords must match.")
        return data

    def validate_old_password(self, value):
        # Validate the old password against the current password
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class GigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gig
        fields = "__all__"
