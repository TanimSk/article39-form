from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Exhibitions, Events, CouraselImages, Stories, TicketBookings, ShowBookingInformation, Albums, Singles, Shows
from .serializers import ShowsSerializer, EventsSerializer, ExhibitionsSerializer, CouraselImagesSerializer, StoriesSerializer, TicketBookingsSerializer, AlbumsSerializer, SinglesSerializer, ShowBookingInformationSerializer, StoriesSerializerShort

from django.conf import settings

# Middleware for checking if the user has admin permission
def check_admin(request):
    if request.user and request.user.is_authenticated:
        if request.user.is_admin:
            return True
        else:
            return False
    return False

class CouraselImagesView(APIView):
    def get(self, request, *args, **kwargs):
        courasel_images = CouraselImages.objects.filter(selected=True).order_by("-created_at")
        serializer = CouraselImagesSerializer(courasel_images, many=True)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )
    
    def post(self, request):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
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
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
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
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
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
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
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
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        story_id = request.GET.get("id", None)
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
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Delete Story with specified ID
        story_id = request.GET.get("id", None)
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
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
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

    def put(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        event_id = request.GET.get("id", None)
        if event_id:
            try:
                event = Events.objects.get(id=event_id)
                event.title = request.data.get("title", event.title)
                event.description = request.data.get("description", event.description)
                event.cover_image = request.data.get("cover_image", event.cover_image)
                event.ticket_price = request.data.get("ticket_price", event.ticket_price)
                event.date = request.data.get("date", event.date)
                event.location = request.data.get("location", event.location)
                event.save()
                serializer = EventsSerializer(event)
                return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
            except Events.DoesNotExist:
                return Response(
                    {"success": False, "message": "Event not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No event ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        event_id = request.GET.get("id", None)
        if event_id:
            try:
                Events.objects.get(id=event_id).delete()
                return Response(
                    {"success": True, "message": "Event deleted"},
                    status=status.HTTP_200_OK,
                )
            except Events.DoesNotExist:
                return Response(
                    {"success": False, "message": "Event not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No event ID provided"},
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
    
    def put(self, request, *args, **kwargs):
        ticket_booking_id = request.GET.get("id", None)
        if ticket_booking_id:
            try:
                ticket_booking = TicketBookings.objects.get(id=ticket_booking_id)
                ticket_booking.event = request.data.get("event", ticket_booking.event)
                ticket_booking.buyer_name = request.data.get("buyer_name", ticket_booking.buyer_name)
                ticket_booking.buyer_email = request.data.get("buyer_email", ticket_booking.buyer_email)
                ticket_booking.buyer_phone = request.data.get("buyer_phone", ticket_booking.buyer_phone)
                ticket_booking.number_of_tickets = request.data.get("number_of_tickets", ticket_booking.number_of_tickets)
                ticket_booking.save()
                serializer = TicketBookingsSerializer(ticket_booking)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except TicketBookings.DoesNotExist:
                return Response(
                    {"success": False, "message": "Ticket booking not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No ticket booking ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        ticket_booking_id = request.GET.get("id", None)
        if ticket_booking_id:
            try:
                TicketBookings.objects.get(id=ticket_booking_id).delete()
                return Response(
                    {"success": True, "message": "Ticket booking deleted"},
                    status=status.HTTP_200_OK,
                )
            except TicketBookings.DoesNotExist:
                return Response(
                    {"success": False, "message": "Ticket booking not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No ticket booking ID provided"},
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
            exhibitions = Exhibitions.objects.all().order_by("-created_at")[offset:offset+perPage]
            total_exhibitions = Exhibitions.objects.count()
            total_pages = total_exhibitions // perPage + (1 if total_exhibitions % perPage else 0)
            serializer = ExhibitionsSerializer(exhibitions, many=True)
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
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
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
    
    def put(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        exhibition_id = request.GET.get("id", None)
        if exhibition_id:
            try:
                exhibition = Exhibitions.objects.get(id=exhibition_id)
                exhibition.title = request.data.get("title", exhibition.title)
                exhibition.description = request.data.get("description", exhibition.description)
                exhibition.cover_image = request.data.get("cover_image", exhibition.cover_image)
                exhibition.date = request.data.get("date", exhibition.date)
                exhibition.from_time = request.data.get("from_time", exhibition.from_time)
                exhibition.to_time = request.data.get("to_time", exhibition.to_time)
                exhibition.location = request.data.get("location", exhibition.location)
                exhibition.tags = request.data.get("tags", exhibition.tags)
                exhibition.author = request.data.get("author", exhibition.author)
                exhibition.save()
                serializer = ExhibitionsSerializer(exhibition)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exhibitions.DoesNotExist:
                return Response(
                    {"success": False, "message": "Exhibition not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No exhibition ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        exhibition_id = request.GET.get("id", None)
        if exhibition_id:
            try:
                Exhibitions.objects.get(id=exhibition_id).delete()
                return Response(
                    {"success": True, "message": "Exhibition deleted"},
                    status=status.HTTP_200_OK,
                )
            except Exhibitions.DoesNotExist:
                return Response(
                    {"success": False, "message": "Exhibition not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No exhibition ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AlbumView(APIView):
    def get(self, request, *args, **kwargs):
        album_id = request.GET.get("id", None)
        if album_id:
            try:
                album = Albums.objects.get(id=album_id)
                serializer = AlbumsSerializer(album)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Albums.DoesNotExist:
                return Response(
                    {"success": False, "message": "Album not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            #Paginate albums
            perPage = request.GET.get("perPage", 10)
            page = request.GET.get("page", 1)
            offset = (page - 1) * perPage
            albums = Albums.objects.all().order_by("-created_at")[offset:offset+perPage]
            total_albums = Albums.objects.count()
            total_pages = total_albums // perPage + (1 if total_albums % perPage else 0)
            serializer = AlbumsSerializer(albums, many=True)
            return Response(
                {"success": True, "data": {
                    "albums": serializer.data,
                    "total": total_albums,
                    "perPage": perPage,
                    "page": page,
                    "totalPage": total_pages,
                    "isLastPage": page==total_pages
                }}, status=status.HTTP_200_OK
            )
    
    def post(self, request):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = AlbumsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"success": True, "data":serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def put(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        album_id = request.GET.get("id", None)
        if album_id:
            try:
                album = Albums.objects.get(id=album_id)
                album.title = request.data.get("title", album.title)
                album.description = request.data.get("description", album.description)
                album.cover_image = request.data.get("cover_image", album.cover_image)
                album.genre = request.data.get("genre", album.genre)
                album.category = request.data.get("category", album.category)
                album.artist = request.data.get("artist", album.artist)
                album.number_of_songs = request.data.get("number_of_songs", album.number_of_songs)
                album.author = request.data.get("author", album.author)
                album.tags = request.data.get("tags", album.tags)
                album.save()
                serializer = AlbumsSerializer(album)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Albums.DoesNotExist:
                return Response(
                    {"success": False, "message": "Album not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No album ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        album_id = request.GET.get("id", None)
        if album_id:
            try:
                Albums.objects.get(id=album_id).delete()
                return Response(
                    {"success": True, "message": "Album deleted"},
                    status=status.HTTP_200_OK,
                )
            except Albums.DoesNotExist:
                return Response(
                    {"success": False, "message": "Album not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No album ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class SinglesView(APIView):
    def get(self, request, *args, **kwargs):
        single_id = request.GET.get("id", None)
        if single_id:
            try:
                single = Singles.objects.get(id=single_id)
                serializer = SinglesSerializer(single)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Singles.DoesNotExist:
                return Response(
                    {"success": False, "message": "Single not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            #Paginate singles
            perPage = request.GET.get("perPage", 10)
            page = request.GET.get("page", 1)
            offset = (page - 1) * perPage
            singles = Singles.objects.all().order_by("-created_at")[offset:offset+perPage]
            total_singles = Singles.objects.count()
            total_pages = total_singles // perPage + (1 if total_singles % perPage else 0)
            serializer = SinglesSerializer(singles, many=True)
            return Response(
                {"success": True, "data": {
                    "singles": serializer.data,
                    "total": total_singles,
                    "perPage": perPage,
                    "page": page,
                    "totalPage": total_pages,
                    "isLastPage": page==total_pages
                }}, status=status.HTTP_200_OK
            )
    
    def post(self, request):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = SinglesSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"success": True, "data":serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        single_id = request.GET.get("id", None)
        if single_id:
            try:
                single = Singles.objects.get(id=single_id)
                single.title = request.data.get("title", single.title)
                single.description = request.data.get("description", single.description)
                single.cover_image = request.data.get("cover_image", single.cover_image)
                single.genre = request.data.get("genre", single.genre)
                single.category = request.data.get("category", single.category)
                single.artist = request.data.get("artist", single.artist)
                single.number_of_songs = request.data.get("number_of_songs", single.number_of_songs)
                single.author = request.data.get("author", single.author)
                single.tags = request.data.get("tags", single.tags)
                single.save()
                serializer = SinglesSerializer(single)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Singles.DoesNotExist:
                return Response(
                    {"success": False, "message": "Single not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No single ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        single_id = request.GET.get("id", None)
        if single_id:
            try:
                Singles.objects.get(id=single_id).delete()
                return Response(
                    {"success": True, "message": "Single deleted"},
                    status=status.HTTP_200_OK,
                )
            except Singles.DoesNotExist:
                return Response(
                    {"success": False, "message": "Single not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No single ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class ShowsView(APIView):
    def get(self, request, *args, **kwargs):
        show_id = request.GET.get("id", None)
        if show_id:
            try:
                show = Shows.objects.get(id=show_id)
                serializer = ShowsSerializer(show)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Shows.DoesNotExist:
                return Response(
                    {"success": False, "message": "Show not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            #Paginate shows
            perPage = request.GET.get("perPage", 10)
            page = request.GET.get("page", 1)
            offset = (page - 1) * perPage
            shows = Shows.objects.all().order_by("-created_at")[offset:offset+perPage]
            total_shows = Shows.objects.count()
            total_pages = total_shows // perPage + (1 if total_shows % perPage else 0)
            serializer = ShowsSerializer(shows, many=True)
            return Response(
                {"success": True, "data": {
                    "shows": serializer.data,
                    "total": total_shows,
                    "perPage": perPage,
                    "page": page,
                    "totalPage": total_pages,
                    "isLastPage": page==total_pages
                }}, status=status.HTTP_200_OK
            )
    
    def post(self, request):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ShowsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"success": True, "data":serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def put(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        show_id = request.GET.get("id", None)
        if show_id:
            try:
                show = Shows.objects.get(id=show_id)
                show.title = request.data.get("title", show.title)
                show.cover_image = request.data.get("cover_image", show.cover_image)
                show.video_url = request.data.get("video_url", show.video_url)
                show.location = request.data.get("location", show.location)
                show.time = request.data.get("time", show.time)
                show.date = request.data.get("date", show.date)
                show.save()
                serializer = ShowsSerializer(show)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Shows.DoesNotExist:
                return Response(
                    {"success": False, "message": "Show not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No show ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        show_id = request.GET.get("id", None)
        if show_id:
            try:
                Shows.objects.get(id=show_id).delete()
                return Response(
                    {"success": True, "message": "Show deleted"},
                    status=status.HTTP_200_OK,
                )
            except Shows.DoesNotExist:
                return Response(
                    {"success": False, "message": "Show not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No show ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ShowBookingInformationView(APIView):
    def get(self, request, *args, **kwargs):
        show_booking_information_id = request.GET.get("id", None)
        if show_booking_information_id:
            try:
                show_booking_information = ShowBookingInformation.objects.get(id=show_booking_information_id)
                serializer = ShowBookingInformationSerializer(show_booking_information)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ShowBookingInformation.DoesNotExist:
                return Response(
                    {"success": False, "message": "Show booking information not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            #Paginate show booking information
            perPage = request.GET.get("perPage", 10)
            page = request.GET.get("page", 1)
            offset = (page - 1) * perPage
            show_booking_informations = ShowBookingInformation.objects.all().order_by("-created_at")[offset:offset+perPage]
            total_show_booking_informations = ShowBookingInformation.objects.count()
            total_pages = total_show_booking_informations // perPage + (1 if total_show_booking_informations % perPage else 0)
            serializer = ShowBookingInformationSerializer(show_booking_informations, many=True)
            return Response(
                {"success": True, "data": {
                    "show_booking_informations": serializer.data,
                    "total": total_show_booking_informations,
                    "perPage": perPage,
                    "page": page,
                    "totalPage": total_pages,
                    "isLastPage": page==total_pages
                }}, status=status.HTTP_200_OK
            )
    
    def post(self, request):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ShowBookingInformationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"success": True, "data":serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def put(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        show_booking_information_id = request.GET.get("id", None)
        if show_booking_information_id:
            try:
                show_booking_information = ShowBookingInformation.objects.get(id=show_booking_information_id)
                show_booking_information.full_name = request.data.get("full_name", show_booking_information.full_name)
                show_booking_information.email = request.data.get("email", show_booking_information.email)
                show_booking_information.phone = request.data.get("phone", show_booking_information.phone)
                show_booking_information.dates = request.data.get("dates", show_booking_information.dates)
                show_booking_information.genre = request.data.get("genre", show_booking_information.genre)
                show_booking_information.save()
                serializer = ShowBookingInformationSerializer(show_booking_information)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ShowBookingInformation.DoesNotExist:
                return Response(
                    {"success": False, "message": "Show booking information not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No show booking information ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, *args, **kwargs):
        if not check_admin(request):
            return Response(
                {"success": False, "message": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        show_booking_information_id = request.GET.get("id", None)
        if show_booking_information_id:
            try:
                ShowBookingInformation.objects.get(id=show_booking_information_id).delete()
                return Response(
                    {"success": True, "message": "Show booking information deleted"},
                    status=status.HTTP_200_OK,
                )
            except ShowBookingInformation.DoesNotExist:
                return Response(
                    {"success": False, "message": "Show booking information not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"success": False, "message": "No show booking information ID provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

