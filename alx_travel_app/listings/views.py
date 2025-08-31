from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing listings.
    Allows CRUD operations on listings.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Set the owner of the listing to the current user.
        """
        serializer.save(owner=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing bookings.
    Allows CRUD operations on bookings.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Set the user of the booking to the current user.
        """
        serializer.save(user=self.request.user)