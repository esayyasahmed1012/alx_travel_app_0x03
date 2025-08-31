from rest_framework import serializers
from .models import Listing, Booking
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ListingSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'location', 'price_per_night', 'owner', 'created_at']

class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source='listing', write_only=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'listing_id', 'user', 'user_id', 'start_date', 'end_date', 'total_price', 'created_at']