from rest_framework import serializers
from website.models import Albums, Singles, Shows, Events, Exhibitions, CouraselImages, Stories, TicketBookings, ShowBookingInformation

class AlbumsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = '__all__'
        
class SinglesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Singles
        fields = '__all__'
        
class ShowsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shows
        fields = '__all__'
        
class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = '__all__'
        
class ExhibitionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exhibitions
        fields = '__all__'

class CouraselImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouraselImages
        fields = '__all__'
        
class StoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stories
        fields = '__all__'

class StoriesSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = Stories
        fields = ['id', 'title', 'cover_image', 'author', 'created_at']
        
class TicketBookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketBookings
        fields = '__all__'

class ShowBookingInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowBookingInformation
        fields = '__all__'

