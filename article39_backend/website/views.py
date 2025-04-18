from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Exhibitions, Events, CouraselImages, Stories, TicketBookings, ShowBookingInformation, Albums, Singles, Shows
from .serializers import ShowsSerializer, EventsSerializer, ExhibitionsSerializer, CouraselImagesSerializer, StoriesSerializer, TicketBookingsSerializer, AlbumsSerializer, SinglesSerializer, ShowBookingInformationSerializer, StoriesSerializerShort, ExhibitionsSerializerShort

from django.conf import settings

class CouraselImagesView(APIView):
    def get(self, request, *args, **kwargs):
        courasel_images = CouraselImages.objects.filter(selected=True).order_by("-created_at")
        serializer = CouraselImagesSerializer(courasel_images, many=True)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )
    
    def post(self, request):
        serializer = CouraselImagesSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"success": True, "data":serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def put(self, request):
        # Update selected status of Courasel images
        courasel_image_id = request.data.get("id", None)
        if courasel_image_id:
            try:
                courasel_image = CouraselImages.objects.get(id=courasel_image_id)
                courasel_image.selected = request.data.get("selected", False)
                courasel_image.save()
                serializer = CouraselImagesSerializer(courasel_image)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CouraselImages.DoesNotExist:
                return Response(
                    {"success": False, "message": "Courasel image not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No Courasel image ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request):
        # Delete Courasel image
        courasel_image_id = request.data.get("id", None)
        if courasel_image_id:
            try:
                CouraselImages.objects.get(id=courasel_image_id).delete()
                return Response(
                    {"success": True, "message": "Courasel image deleted"},
                    status=status.HTTP_200_OK,
                )
            except CouraselImages.DoesNotExist:
                return Response(
                    {"success": False, "message": "Courasel image not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No Courasel image ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class StoriesView(APIView):
    def get(self, request, *args, **kwargs):
        story_id = request.GET.get("id", None)
        if story_id:
            try:
                story = Stories.objects.get(id=story_id)
                serializer = StoriesSerializer(story)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Stories.DoesNotExist:
                return Response(
                    {"success": False, "message": "Story not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            #Paginate stories
            perPage = request.GET.get("perPage", 10)
            page = request.GET.get("page", 1)
            offset = (page - 1) * perPage
            stories = Stories.objects.all().values("id", "title", "cover_image", "author", "created_at").order_by("-created_at")[offset:offset+perPage]
            total_stories = Stories.objects.count()
            total_pages = total_stories // perPage + (1 if total_stories % perPage else 0)
            serializer = StoriesSerializerShort(stories, many=True)
            return Response(
                {"success": True, "data": {
                    "stories": serializer.data,
                    "total": total_stories,
                    "perPage": perPage,
                    "page": page,
                    "totalPage": total_pages,
                    "isLastPage": page==total_pages
                }}, status=status.HTTP_200_OK
            )
    
    def post(self, request):
        serializer = StoriesSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"success": True, "data":serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def put(self, request):
        # Update Courasel image
        story_id = request.data.get("id", None)
        if story_id:
            try:
                story = Stories.objects.get(id=story_id)
                story.title = request.data.get("title", story.title)
                story.cover_image = request.data.get("cover_image", story.cover_image)
                story.author = request.data.get("author", story.author)
                story.content = request.data.get("content", story.content)
                story.tags = request.data.get("tags", story.tags)
                story.save()
                serializer = StoriesSerializer(story)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Stories.DoesNotExist:
                return Response(
                    {"success": False, "message": "Story not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No story ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request):
        # Delete Story with specified ID
        story_id = request.data.get("id", None)
        if story_id:
            try:
                Stories.objects.get(id=story_id).delete()
                return Response(
                    {"success": True, "message": "Story deleted"},
                    status=status.HTTP_200_OK,
                )
            except Stories.DoesNotExist:
                return Response(
                    {"success": False, "message": "Story not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No story ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class EventsView(APIView):
    def get(self, request, *args, **kwargs):
        event_id = request.GET.get("id", None)
        if event_id:
            try:
                event = Events.objects.get(id=event_id)
                serializer = EventsSerializer(event)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Events.DoesNotExist:
                return Response(
                    {"success": False, "message": "Event not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            #Paginate events
            perPage = request.GET.get("perPage", 10)
            page = request.GET.get("page", 1)
            offset = (page - 1) * perPage
            events = Events.objects.all().order_by("-created_at")[offset:offset+perPage]
            total_events = Events.objects.count()
            total_pages = total_events // perPage + (1 if total_events % perPage else 0)
            serializer = EventsSerializer(events, many=True)
            return Response(
                {"success": True, "data": {
                    "events": serializer.data,
                    "total": total_events,
                    "perPage": perPage,
                    "page": page,
                    "totalPage": total_pages,
                    "isLastPage": page==total_pages
                }}, status=status.HTTP_200_OK
            )
    
    def post(self, request):
        serializer = EventsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"success": True, "data":serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

class TicketBookingsView(APIView):
    def get(self, request, *args, **kwargs):
        ticket_booking_id = request.GET.get("id", None)
        if ticket_booking_id:
            try:
                ticket_booking = TicketBookings.objects.get(id=ticket_booking_id)
                serializer = TicketBookingsSerializer(ticket_booking)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except TicketBookings.DoesNotExist:
                return Response(
                    {"success": False, "message": "Ticket booking not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            #Paginate ticket bookings
            perPage = request.GET.get("perPage", 10)
            page = request.GET.get("page", 1)
            offset = (page - 1) * perPage
            ticket_bookings = TicketBookings.objects.all().order_by("-created_at")[offset:offset+perPage]
            total_ticket_bookings = TicketBookings.objects.count()
            total_pages = total_ticket_bookings // perPage + (1 if total_ticket_bookings % perPage else 0)
            serializer = TicketBookingsSerializer(ticket_bookings, many=True)
            return Response(
                {"success": True, "data": {
                    "ticket_bookings": serializer.data,
                    "total": total_ticket_bookings,
                    "perPage": perPage,
                    "page": page,
                    "totalPage": total_pages,
                    "isLastPage": page==total_pages
                }}, status=status.HTTP_200_OK
            )
    
    def post(self, request):
        serializer = TicketBookingsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"success": True, "data":serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

class ExhibitionsView(APIView):
    def get(self, request, *args, **kwargs):
        exhibition_id = request.GET.get("id", None)
        if exhibition_id:
            try:
                exhibition = Exhibitions.objects.get(id=exhibition_id)
                serializer = ExhibitionsSerializer(exhibition)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exhibitions.DoesNotExist:
                return Response(
                    {"success": False, "message": "Exhibition not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            #Paginate exhibitions
            perPage = request.GET.get("perPage", 10)
            page = request.GET.get("page", 1)
            offset = (page - 1) * perPage
            exhibitions = Exhibitions.objects.all().values("id", "title", "cover_image", "date", "from_time", "to_time", "location", "author", "created_at").order_by("-created_at")[offset:offset+perPage]
            total_exhibitions = Exhibitions.objects.count()
            total_pages = total_exhibitions // perPage + (1 if total_exhibitions % perPage else 0)
            serializer = ExhibitionsSerializerShort(exhibitions, many=True)
            return Response(
                {"success": True, "data": {
                    "exhibitions": serializer.data,
                    "total": total_exhibitions,
                    "perPage": perPage,
                    "page": page,
                    "totalPage": total_pages,
                    "isLastPage": page==total_pages
                }}, status=status.HTTP_200_OK
            )
    
    def post(self, request):
        serializer = ExhibitionsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"success": True, "data":serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

