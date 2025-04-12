from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from administrator.models import Gig
from artist.serializers import GigApplicationSerializer


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

    def to_representation(self, instance):
        # Call the parent method to get the base representation of the instance
        instance_rep = super().to_representation(instance)

        # Get the request from the context
        request = self.context.get("request")

        # Check if the user is authenticated
        if request and request.user.is_authenticated:
            # Serialize the related GigApplication instances for the current user
            applications = GigApplicationSerializer(
                instance.applications.filter(user=request.user.artist_profile),
                many=True,
                context=self.context,
            ).data
            instance_rep["applications"] = applications
        else:
            # If the user is not authenticated, set applications to an empty list
            instance_rep["applications"] = []

        return instance_rep
